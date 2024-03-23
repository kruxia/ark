
CREATE TABLE content (
    id          uuid    not null default gen_random_uuid(),
    version_id  uuid    not null references version(id),
    PRIMARY KEY (id, version_id),

    project_id  uuid    not null references project(id),
    mimetype    text    not null references mimetype(name) default 'application/octet-stream',
    size        bigint  not null default 0,
    path        text    not null,
    title       text,
    meta        jsonb
);

CREATE INDEX content_project_id_idx ON content(project_id);
CREATE UNIQUE INDEX content_path_idx ON content(project_id, path);
