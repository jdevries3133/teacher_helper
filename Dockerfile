# For documentation site container
FROM python:3.10-alpine as build

WORKDIR /app

COPY mkdocs.yml .
COPY requirements.docs.txt .
RUN pip install -r requirements.docs.txt
RUN mkdir docs
COPY docs docs
RUN mkdocs build

FROM nginx:1.21-alpine

WORKDIR /usr/share/nginx/html
COPY --from=build /app/site .

ENTRYPOINT ["nginx", "-g", "daemon off;"]

# {% comment %}
# vi:filetype=dockerfile
# {% endcomment %}
