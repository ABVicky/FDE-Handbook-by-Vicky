# Module 04 — Exercises

| # | Exercise | After lesson | Solution |
| --- | --- | --- | --- |
| 01 | [Design the campus-visits API](01-api-design.md) | 02 | [solutions/01-api-design.md](solutions/01-api-design.md) |
| 02 | [A FastAPI course catalogue with auth and tests](02-fastapi-service.md) | 03–05 | [`course_service.py`](solutions/course_service.py), [`test_course_service.py`](solutions/test_course_service.py) |
| 03 | [A React `CourseFilter` component](03-react-component.md) | 06–07 | [`CourseFilter.tsx`](solutions/CourseFilter.tsx), [`CourseFilter.test.tsx`](solutions/CourseFilter.test.tsx) |
| 04 | [Review a pull request](04-code-review.md) | 09 | [solutions/04-code-review.md](solutions/04-code-review.md) |

Run the Python solution's tests:

```bash
cd modules/04-software-engineering/exercises/solutions
```

```bash
python -m pytest -o addopts="" test_course_service.py
```

(Needs `fastapi`, `httpx` and `pytest` in your venv.)
