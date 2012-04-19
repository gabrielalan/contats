# -*- coding: utf-8 -*-

from sqlite3 import dbapi2 as sqlite3
from contextlib import closing
from flask import Flask, url_for, abort, render_template, g, redirect, flash, request

# ------------------------------------------------------------------------
# Configuracoes

DATABASE 	= 'tmp/contats.db'
SECRET_KEY      = '1234'  
DEBUG 		= True

app = Flask(__name__)

app.config.from_object( __name__ )

# ------------------------------------------------------------------------
# Inicio do DB e funcoes de suporte

def db_connect():
	return sqlite3.connect( app.config['DATABASE'] )
	
def db_init():
	with closing( db_connect() ) as db:
		with app.open_resource( 'banco.sql' ) as sql:
			db.cursor().executescript( sql.read() )
		db.commit()

def get_all():
        query = g.db.execute( 'SELECT * FROM contatos ORDER BY id DESC' )
	
	registros = []
	
	for linha in query.fetchall():
		registros.append(
			{
				"id"		: linha[0],
				"nome"  	: linha[1],
				"sobrenome"	: linha[2],
				"email"		: linha[3],
				"fone"  	: linha[4]
			}
        )

        return registros

def get( id ):
        if not id:
                return False
        
        query = g.db.execute( 'SELECT * FROM contatos WHERE id = ? ORDER BY id DESC LIMIT 1', [ id ] )
	
	registro = query.fetchone()

        contato = {
                "id"            : registro[0],
                "nome"          : registro[1],
                "sobrenome"     : registro[2],
                "email"         : registro[3],
                "fone"          : registro[4],
                "endereco"      : registro[5],
        }
        
        return contato    

# ------------------------------------------------------------------------

@app.before_request
def before_request():
	g.db = db_connect()

@app.teardown_request
def teardown_request( exception ):
	if hasattr( g, 'db' ):
		g.db.close()

# ------------------------------------------------------------------------	

@app.route('/remover/<int:id>')
def remover(id):
        if not id:
                flash( u'Id não informado' )
        else:
                g.db.execute(
                        'DELETE FROM contatos WHERE id = ?',
                        [ id ]
                )

                g.db.commit()
                
                flash( u'Contato removido com sucesso' )
        
        return redirect( url_for( 'index' ) )

@app.route('/salvar', methods = ['POST'])
def salvar():
        id_editar       = request.form['id']
        nome            = request.form['nome']
        sobrenome       = request.form['sobrenome']
        email           = request.form['email']
        fone            = request.form['fone']
        endereco        = request.form['endereco']

        if not nome or not email:
                flash( u'Nome e E-mail são obrigatórios' )
        else:
                if not id_editar:
                        g.db.execute(
                                'INSERT INTO contatos (nome, sobrenome, email, fone, endereco) VALUES (?, ?, ?, ?, ?)',
                                [ nome, sobrenome, email, fone, endereco ]
                        )

                        acao = 'cadastrado'
                else:
                        g.db.execute(
                                'UPDATE contatos SET nome = ?, sobrenome = ?, email = ?, fone = ?, endereco = ? WHERE id = ?',
                                [ nome, sobrenome, email, fone, endereco, id_editar ]
                        )

                        acao = 'modificado'

                g.db.commit()
                
                flash( u'Contato %s com sucesso' % acao )

        return redirect( url_for( 'index' ) )

@app.route('/editar/<int:id>')
def editar( id ):
        registros = get_all()

        if not id:
                flash( u'Id nao informado' )

                return redirect( url_for( 'index' ) )
        else:
                registro = get( id )
        
        return render_template('index.html', contatos = registros, contato = registro)

@app.route('/')
def index():
	registros = get_all()
        
        return render_template('index.html', contatos = registros)

# ------------------------------------------------------------------------

if __name__ == '__main__':
        app.run()
