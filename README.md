# hcd-chatbot

To run Dockerfile:

```bash
docker build -t hcd-chatbot .
docker run --env-file .env -p 5000:5000 hcd-chatbot
```

To add package to poetry package:

```bash
poetry add 'package_name'
poetry lock
```
