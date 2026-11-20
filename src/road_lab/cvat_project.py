"""cvat_project: tự động tạo project CVAT theo taxonomy Road v1.0.

Chỉ dùng thư viện chuẩn Python (urllib). Gọi REST API của CVAT để:

  1. Đăng nhập vào CVAT lớp.
  2. Tạo project ``d11-road-<tên>`` với toàn bộ nhãn từ
     :mod:`src.road_lab.taxonomy` (6 nhãn vẽ + 4 nhãn tag, định dạng CVAT
     "Raw" labels).
  3. Tạo hai task ``front`` và ``fisheye`` dưới project, upload ảnh trong
     ``data/`` vào task tương ứng theo slot tên file (A*=front, B*=fisheye).
  4. In gợi ý tag mặc định cho mỗi ảnh (camera lấy từ tên file; timeofday,
     weather, source học viên chọn tay vì tên file không chứa).

Chạy:

    PYTHONPATH=src python3 -m road_lab.cvat_project \
        --url https://cvat.lop.hoc --user hocvien --password matkhau \
        --name d11-road-ten --data data/ --dry-run

Bỏ ``--dry-run`` để thực thi thật trên CVAT. Cần quyền tạo project/task trên
CVAT của lớp. Ảnh và GT không được đưa lên app.cvat.ai theo quy định lab.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import mimetypes
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .taxonomy import (
    CORE_FRONT,
    CORE_FISHEYE,
    EXTRA_FRONT,
    EXTRA_FISHEYE,
    expected_camera,
    image_slot,
    raw_labels,
)

CVAT_API_VERSION = "1.1"

DEFAULT_IMAGE_QUALITY = 70
DEFAULT_START_FRAME = 0
DEFAULT_STOP_FRAME = 0
DEFAULT_CHUNK_SIZE = 10
DEFAULT_CHUNK_TYPE = "imageset"

_CORE_FRONT_SET = set(CORE_FRONT)
_CORE_FISHEYE_SET = set(CORE_FISHEYE)


class CvatError(RuntimeError):
    """Lỗi khi gọi CVAT API."""


class CvatApi:
    """Client tối thiểu cho CVAT REST API (session cookie qua urllib)."""

    def __init__(self, base_url: str, cookie_jar: http.cookiejar.CookieJar | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.jar = cookie_jar or http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )

    def _csrf_token(self) -> str | None:
        for cookie in self.jar:
            if cookie.name == "csrftoken":
                return cookie.value
        return None

    def _request(
        self,
        method: str,
        path: str,
        payload: Any = None,
        files: list[tuple[str, str, bytes]] | None = None,
        fields: list[tuple[str, str, str]] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        data: bytes | None = None
        headers: dict[str, str] = {}

        if files:
            boundary = "----CvatFormBoundary" + "x" * 16
            parts: list[bytes] = []
            if fields:
                for field_name, _, value in fields:
                    parts.append(f"--{boundary}\r\n".encode())
                    parts.append(f'Content-Disposition: form-data; name="{field_name}"\r\n\r\n'.encode())
                    parts.append(str(value).encode())
                    parts.append(b"\r\n")
            for field_name, filename, body in files:
                parts.append(f"--{boundary}\r\n".encode())
                parts.append(
                    f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode()
                )
                ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
                parts.append(f"Content-Type: {ctype}\r\n\r\n".encode())
                parts.append(body)
                parts.append(b"\r\n")
            parts.append(f"--{boundary}--\r\n".encode())
            data = b"".join(parts)
            headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        elif payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif fields:
            data = urllib.parse.urlencode([(name, value) for name, _, value in fields]).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        csrf = self._csrf_token()
        if csrf:
            headers["X-CSRFToken"] = csrf
        if extra_headers:
            headers.update(extra_headers)

        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with self._opener.open(req) as resp:
                body = resp.read()
                if not body:
                    return None
                return json.loads(body.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise CvatError(f"{method} {path} -> HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise CvatError(f"{method} {path} -> {exc}") from exc

    def login(self, username: str, password: str) -> None:
        self._request("POST", "/api/auth/login", payload={"username": username, "password": password})

    def _unpage(self, payload: Any) -> list[dict]:
        if isinstance(payload, dict) and "results" in payload:
            return payload["results"] or []
        return payload or []

    def get_projects(self) -> list[dict]:
        return self._unpage(self._request("GET", "/api/projects")) or []

    def find_project(self, name: str) -> dict | None:
        for project in self.get_projects():
            if project.get("name") == name:
                return project
        return None

    def create_project(self, name: str, labels: list[dict]) -> dict:
        payload = {"name": name, "labels": labels}
        return self._request("POST", "/api/projects", payload=payload)

    def delete_project(self, project_id: int) -> None:
        self._request("DELETE", f"/api/projects/{project_id}")

    def delete_task(self, task_id: int) -> None:
        self._request("DELETE", f"/api/tasks/{task_id}")

    def ensure_project(self, name: str, labels: list[dict], dry_run: bool = False, reset: bool = False) -> dict | None:
        if dry_run:
            print(f"[dry-run] tao project {name!r} voi {len(labels)} nhan")
            return None
        existing = self.find_project(name)
        if existing:
            if reset:
                # Xoa task cua project truoc, xoa project
                for t in self.get_tasks(existing["id"]):
                    self.delete_task(t["id"])
                    print(f"xoa task cu: id={t['id']} name={t.get('name')!r}")
                self.delete_project(existing["id"])
                print(f"xoa project cu: id={existing['id']} name={name!r}")
            else:
                print(f"project da ton tai: id={existing['id']} name={name!r}")
                return existing
        created = self.create_project(name, labels)
        print(f"tao project xong: id={created.get('id')} name={name!r}")
        return created

    def get_tasks(self, project_id: int) -> list[dict]:
        return self._unpage(
            self._request("GET", "/api/tasks", extra_headers={"X-Project-Id": str(project_id)})
        ) or []

    def find_task(self, project_id: int, name: str) -> dict | None:
        for task in self.get_tasks(project_id):
            if task.get("name") == name:
                return task
        return None

    def create_task(self, name: str, project_id: int, labels: list[dict]) -> dict:
        payload = {
            "name": name,
            "project_id": project_id,
            "image_quality": DEFAULT_IMAGE_QUALITY,
            "start_frame": DEFAULT_START_FRAME,
            "stop_frame": DEFAULT_STOP_FRAME,
            "chunk_size": DEFAULT_CHUNK_SIZE,
            "chunk_type": DEFAULT_CHUNK_TYPE,
        }
        return self._request("POST", "/api/tasks", payload=payload)

    def upload_data(self, task_id: int, image_paths: list[Path], dry_run: bool = False) -> None:
        if dry_run:
            print(f"[dry-run] upload {len(image_paths)} anh vao task {task_id}")
            return
        url = f"/api/tasks/{task_id}/data"
        fields = [
            ("image_quality", "", str(DEFAULT_IMAGE_QUALITY)),
            ("sorting_method", "", "predefined"),
        ]
        # CVAT dung giao thuc "CVAT-TUS": Upload-Start -> Upload-Multiple -> Upload-Finish
        self._request("POST", url, extra_headers={"Upload-Start": ""})
        files = [(f"client_files[{i}]", p.name, p.read_bytes()) for i, p in enumerate(image_paths)]
        self._request(
            "POST",
            url,
            files=files,
            fields=fields,
            extra_headers={"Upload-Multiple": ""},
        )
        resp = self._request("POST", url, fields=fields, extra_headers={"Upload-Finish": ""})
        rq_id = None
        if isinstance(resp, dict):
            rq_id = resp.get("rq_id")
        if rq_id:
            print(f"da gui yeu cau upload {len(image_paths)} anh vao task {task_id} (rq_id={rq_id})")
        else:
            print(f"da gui yeu cau upload {len(image_paths)} anh vao task {task_id}")
        # Doc lai task de kiem tra size (CVAT xu ly upload trong background qua RQ worker)
        for _ in range(120):
            time.sleep(1)
            task = self._request("GET", f"/api/tasks/{task_id}")
            if task and task.get("size", 0) >= len(image_paths):
                print(f"task {task_id} co {task['size']} anh san sang")
                return
        print(
            f"LOI: task {task_id} chua du anh sau 120s. "
            f"Kiem tra log worker: docker logs cvat_worker_import --tail 50",
            file=sys.stderr,
        )


def _collect_images(data_dir: Path, core_only: bool) -> tuple[list[Path], list[Path]]:
    """Tra ve (front_images, fisheye_images) sap xep theo ten."""
    front: list[Path] = []
    fisheye: list[Path] = []
    for path in sorted(data_dir.iterdir()):
        if not path.is_file():
            continue
        slot = image_slot(path.name)
        if slot is None:
            continue
        if core_only:
            if slot.startswith("A") and slot not in _CORE_FRONT_SET:
                continue
            if slot.startswith("B") and slot not in _CORE_FISHEYE_SET:
                continue
        if slot.startswith("A"):
            front.append(path)
        elif slot.startswith("B"):
            fisheye.append(path)
    return front, fisheye


def _default_tags(path: Path) -> dict[str, str]:
    """Gia tri tag khuyen nghich lay tu ten file (chi camera xac dinh duoc)."""
    slot = image_slot(path.name) or ""
    tags: dict[str, str] = {}
    if slot.startswith("A"):
        tags["camera"] = "front"
    elif slot.startswith("B"):
        tags["camera"] = expected_camera(path.name) or ""
    tags.setdefault("timeofday", "")
    tags.setdefault("weather", "")
    tags.setdefault("source", "")
    return tags


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="cvat_project",
        description="Tao tu dong project CVAT theo taxonomy Road v1.0.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--url", required=True, help="Dia chi CVAT lop, vi du https://cvat.lop.hoc")
    ap.add_argument("--user", required=True, help="Tai khoan CVAT")
    ap.add_argument("--password", required=True, help="Mat khau CVAT")
    ap.add_argument("--name", required=True, help="Ten project, vi du d11-road-ten")
    ap.add_argument("--data", default="data", help="Thu muc chua anh (mac dinh: data)")
    ap.add_argument(
        "--front-task", default="front", help="Ten task front (mac dinh: front)"
    )
    ap.add_argument(
        "--fisheye-task", default="fisheye", help="Ten task fisheye (mac dinh: fisheye)"
    )
    ap.add_argument(
        "--core-only",
        action="store_true",
        help="Chi xu ly anh bat buoc A01-A12 va B01-B08",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Chi in thao tap se lam, khong goi API CVAT thuc su",
    )
    ap.add_argument(
        "--reset",
        action="store_true",
        help="Xoa project/task cu ten trung lap truoc khi tao moi",
    )
    args = ap.parse_args(argv)

    data_dir = Path(args.data)
    if not data_dir.is_dir():
        print(f"Thu muc khong ton tai: {data_dir}", file=sys.stderr)
        return 2

    labels = raw_labels()
    front_images, fisheye_images = _collect_images(data_dir, args.core_only)

    print(f"Tim {len(front_images)} anh front va {len(fisheye_images)} anh fisheye trong {data_dir}")
    if not front_images and not fisheye_images:
        print("Khong co anh nao hop le de upload.", file=sys.stderr)
        return 2

    api = CvatApi(args.url)
    if not args.dry_run:
        api.login(args.user, args.password)
        print("dang nhap CVAT thanh cong")

    project = api.ensure_project(args.name, labels, dry_run=args.dry_run, reset=args.reset)
    project_id = project.get("id") if project else None

    if project_id is None and not args.dry_run:
        print("Khong xac dinh duoc id project de tao task.", file=sys.stderr)
        return 2

    tasks: list[tuple[str, str, list[Path]]] = [
        (args.front_task, "front", front_images),
        (args.fisheye_task, "fisheye", fisheye_images),
    ]

    for task_name, camera_group, images in tasks:
        if not images:
            print(f"bo qua task {task_name!r} (khong co anh)")
            continue
        if args.dry_run:
            print(f"[dry-run] tao task {task_name!r} va upload {len(images)} anh")
            for p in images:
                tags = _default_tags(p)
                print(f"  {p.name} -> camera={tags.get('camera','')!r}")
            continue
        assert project_id is not None
        existing = api.find_task(project_id, task_name)
        if existing:
            if args.reset:
                api.delete_task(existing["id"])
                print(f"xoa task cu: id={existing['id']} name={task_name!r}")
                created = api.create_task(task_name, project_id, labels)
                task_id = created.get("id")
                print(f"tao task moi: id={task_id} name={task_name!r}")
            else:
                task_id = existing["id"]
                print(f"task da ton tai: id={task_id} name={task_name!r}")
        else:
            created = api.create_task(task_name, project_id, labels)
            task_id = created.get("id")
            print(f"tao task xong: id={task_id} name={task_name!r}")
        api.upload_data(task_id, images, dry_run=False)

    print("\nGhi nho: tag timeofday/weather/source chua xac dinh tu ten file, hoc vien chon tay trong CVAT.")
    print("Sau khi xong, export dinh dang 'CVAT for images 1.1' (khong kem anh) va chay:")
    print("  PYTHONPATH=src python3 -m road_lab.road_check lint <ten>-front.zip <ten>-fisheye.zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
