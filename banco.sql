drop table if exists contatos;
create table contatos (
  id integer primary key autoincrement,
  nome string not null,
  sobrenome string not null,
  email string not null,
  fone string not null,
  endereco string not null
);