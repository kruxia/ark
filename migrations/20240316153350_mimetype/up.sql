
CREATE TABLE mimetype (
    name    varchar primary key    
);

CREATE TABLE ext_mimetype (
    ext     varchar primary key,
    name    varchar not null references mimetype(name)
);