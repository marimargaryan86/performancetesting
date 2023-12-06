files(
    name="source_files",
    sources=["**/*", "!build/**/*", "!node_modules/**/*", "!openapi/**/*"],
)
custom_image(
    prefix="docs",
    dependencies=[
        "//openapi/junction/client_api:client_api",
        "//openapi/junction/data_api:data_api",
        "//openapi/junction/mobile_api:mobile_api",
        "//openapi/junction/pay_admin_api:pay_admin_api",
        "//openapi/junction/pay_api:pay_api",
        "//openapi/junction/plus_poc_api:plus_poc_api",
        "//openapi/junction/hub_api:hub_api",
        ":source_files",
    ],
    instructions=[
        "ARG REGISTRY",
        (
            "FROM ${REGISTRY}node@sha256:4e271ab266a4b76874c8e7c8aa431a8dbe636af19fa5e76403e3acbd9b8d3450"
            " AS build"
        ),
        "WORKDIR /src",
        "COPY docs/engineering/package.json docs/engineering/package-lock.json /src/",
        "RUN npm ci",
        "COPY docs/engineering /src",
        "RUN npm run build",
        "ARG REGISTRY",
        (
            "FROM ${REGISTRY}nginx@sha256:f2fee5c7194cbbfb9d2711fa5de094c797a42a51aa42b0c8ee8ca31547c872b1"
            " AS runtime"
        ),
        "COPY --from=build /src/build /usr/share/nginx/html",
        "# hadolint ignore=SC2016",
        (
            'RUN mkdir -p /etc/nginx/templates/ && printf "server {listen'
            " \\${NGINX_PORT};server_name localhost;port_in_redirect off;root"
            ' /usr/share/nginx/html;}" > /etc/nginx/templates/default.conf.template'
        ),
        'ARG VERSION "dev"',
        "ENV VERSION $VERSION",
        'LABEL vendor="Snowfall Limited"',
        "LABEL com.snowfalltravel.version=$VERSION",
    ],
)
