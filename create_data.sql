CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE if not exists public.employee (
    id uuid DEFAULT uuid_generate_v4(),
    name character varying(256) NOT NULL,
    parent character varying(256),
    root character varying(256),
    height integer NOT NULL
);


CREATE TABLE if not exists public.relationship (
    ancestor uuid,
    descendant uuid
);

insert into employee (name, root, height) values ('P0', 'P0', 0);

insert into employee (name, parent, root, height) values ('P01', 'P0', 'P0', 1);
insert into employee (name, parent, root, height) values ('P02', 'P0', 'P0', 1);
insert into employee (name, parent, root, height) values ('P03', 'P0', 'P0', 1);
insert into employee (name, parent, root, height) values ('P04', 'P0', 'P0', 1);
insert into employee (name, parent, root, height) values ('P05', 'P0', 'P0', 1);

insert into employee (name, parent, root, height) values ('P011', 'P01', 'P0', 2);
insert into employee (name, parent, root, height) values ('P012', 'P01', 'P0', 2);
insert into employee (name, parent, root, height) values ('P013', 'P01', 'P0', 2);
insert into employee (name, parent, root, height) values ('P031', 'P03', 'P0', 2);
insert into employee (name, parent, root, height) values ('P032', 'P03', 'P0', 2);
insert into employee (name, parent, root, height) values ('P051', 'P05', 'P0', 2);

insert into employee (name, parent, root, height) values ('P0511', 'P051', 'P0', 3);
insert into employee (name, parent, root, height) values ('P05111','P0511', 'P0', 4);
insert into employee (name, parent, root, height) values ('P051111','P05111', 'P0', 5);
insert into employee (name, parent, root, height) values ('P0511111', 'P051111', 'P0', 6);

insert into employee (name, parent, root, height) values ('P01', 'P051', 'P0', 3);
insert into employee (name, parent, root, height) values ('P777', 'P01', 'P0', 4);


insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P0'), (select id from employee where name = 'P01' and parent='P0'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P0'), (select id from employee where name = 'P02'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P0'), (select id from employee where name = 'P03'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P0'), (select id from employee where name = 'P04'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P0'), (select id from employee where name = 'P05'));

insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P01' and parent='P0'), (select id from employee where name = 'P011'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P01' and parent='P0'), (select id from employee where name = 'P012'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P01' and parent='P0'), (select id from employee where name = 'P013'));

insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P03'), (select id from employee where name = 'P031'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P03'), (select id from employee where name = 'P032'));

insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P05'), (select id from employee where name = 'P051'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P051'), (select id from employee where name = 'P0511'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P0511'), (select id from employee where name = 'P05111'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P05111'), (select id from employee where name = 'P051111'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P051111'), (select id from employee where name = 'P0511111'));

insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P051'), (select id from employee where name = 'P01' and parent='P051'));
insert into relationship (ancestor, descendant) values ((select id from employee where name = 'P01' and parent='P051'), (select id from employee where name = 'P777'));
