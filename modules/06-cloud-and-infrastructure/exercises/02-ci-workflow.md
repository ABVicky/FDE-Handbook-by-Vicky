# Exercise 02 — A CI workflow for the course-catalogue service

In your fork, add `.github/workflows/course-service-ci.yml` that, on pull requests and pushes to `main`:

1. Runs the tests on Python **3.9 and 3.12** (matrix)
2. Builds the Docker image from Exercise 01
3. Starts the image and checks `GET /courses` returns 200
4. Uses `permissions: contents: read`
5. Only runs when the service's files change (`paths:`)

Then open a pull request that breaks a test, and confirm the check fails and blocks merging (after enabling branch protection).
