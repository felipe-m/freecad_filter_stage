# Estructura de subtree para los scripts de Python para diseños FreeCad

En este ejemplo vamos a ver cómo integrar el módulo `comps` de python en otros módulos que lo usen.

La mayor parte de la información se ha obtenido de aquí:
https://andrey.nering.com.br/2016/git-submodules-vs-subtrees/

Aquí también hay info, pero me gusta más la de arriba:

https://medium.com/@porteneuve/mastering-git-subtrees-943d29a798ec


Resumen de la estructura que tengo en mi ordenador local, queremos hacer algo parecido en nuestro ordenador local:

```
py_freecad/              # python scripts for FreeCAD
  +-- comps/               # library of components
      +-- comps.py            # components
      +-- kcomp.py            # constants about components
      +-- fcfun.py            # library of functions
  +-- citometro/          # citometer scripts
      +-- epi3.py         # Utiliza comps
      +-- modules/        # ------ subtree del comps
          +-- comps/
              +-- comps.py
              +-- kcomp.py
              +-- fcfun.py
  +-- freecad_filter_stage/   
      +-- src/
          +-- filter_holder_clss.py  # Utiliza comps
          +-- comps/      # ------ subtree del comps
```

Vamos a crear un nuevo repositorio `mi_pyfcad`, que también use el `comps`.
Lo primero es tener el repositorio `comps` en local. Lo bajamos de internet. Vamos a la carpeta raiz donde lo queremos:

```
py_freecad $ git clone https://github.com/felipe-m/fcad-comps.git comps
```

Ponemos el `comps` al final para que el nombre sea `comps` y no `fcad-comps` que es el nombre que está en el github.

Con esto tenemos todo el módulo `comps` dentro del directorio `py_freecad`
```
py_freecad/              # python scripts for FreeCAD
  +-- comps/               # library of components
      +-- .git/               # carpeta del repositorio git
      +-- comps.py            # components
      +-- kcomp.py            # constants about components
      +-- fcfun.py            # library of functions
      +-- ....
```

Ahora vamos a crear un repositorio que use el módulo `comps`. Lo llamaremos `mi_pyfcad`:

```
py_freecad $ mkdir mi_pyfcad
py_freecad $ cd mi_pyfcad
py_freecad/mi_pyfcad $ git init
```

Ahora ya podemos crear los ficheros. Los podemos crear directamente, o si queremos, los creamos en un directorio de ficheros fuente (src). Vamos a crearlo en un directorio de ficheros fuente:

```
py_freecad/mi_pyfcad (master) $ mkdir src
py_freecad/mi_pyfcad (master) $ cd src
```

En este directorio creamos nuestros ficheros python.
Por ejemplo, vamos a suponer que creamos un fichero `prueba.py` que usa una función de `comps/comps.py`.

Como este fichero `prueba.py` va a utilizar funciones de `comps/comps.py`, al principio tendrá la siguiente sentencia para añadir el path de comps:

```
sys.path.append(filepath + '/../../' + 'comps'
```

Lo que hace esta sentencia es añadir el camino relativo desde `py_freecad/mi_pyfcad/src` a `py_freecad/comps`, es decir
* subir (o bajar, según se mire) de `src` a `mi_pyfcad`
* y de `mi_pyfcad` a `py_freecad`,
* y luego bajar (o subir) a `comps`


Volvemos al directorio raíz de `mi_pyfcad` y hacemos un primer _commit_:

```
py_freecad/mi_pyfcad/src (master) $ cd ..
py_freecad/mi_pyfcad (master) $ git add .
py_freecad/mi_pyfcad (master) $ git commit -m "Initial commit"
```

La estructura que tenemos será:

```
py_freecad/              # python scripts for FreeCAD
  +-- comps/               # library of components
      +-- .git/               # carpeta del repositorio git
      +-- comps.py            # components
      +-- kcomp.py            # constants about components
      +-- fcfun.py            # library of functions
      +-- ....
  +-- mi_pyfcad/
      +-- .git/               # carpeta del repositorio git
      +-- src/
          +--prueba.py        # este fichero usa funciones de ../../comps
```

Tal como lo tenemos ahora, podemos hacer cambios en los ficheros de `mi_pyfcad` y usar las funciones de `comps`.
**Podríamos trabajar así sin problema**.

Sin embargo, podríamos querer tener un _subtree_ de `comps` dentro del repositorio `mi_pyfcad`.
Dos razones que se me ocurren:
* Por mantener sincronizado lo que funciona de `mi_pyfcad` junto con la versión que funciona de `comps`. Es decir, tener una versión conjunta de lo que funciona. Por si quiero volver atrás a una versión anterior de ambos, que conjuntamente funcionen.
* Por necesitar probar cambios en `comps` sin modificar la versión original hasta que los pruebe.

En este caso, puedo hacer un _subtree_:

**Añadimos `comps` como remoto**:

```
py_freecad/mi_pyfcad (master) $ git remote add comps ../comps
```

En el `remote add` se pone `comps` no el camino donde se va a guardar porque es sólo el nombre.
Que puedo verlo. Es un remoto local (no un remoto de github):

```
py_freecad/mi_pyfcad (master) $ git remote -v
comps    ../comps (fetch)
comps    ../comps (push)
```

Ahora añado el _subtree_, que aquí si que pongo el camino donde va a ir, por ejemplo:

```
py_freecad/mi_pyfcad (master) $ git subtree add --squash --prefix=src/comps/ comps master
```

Con esto, se ha creado/copiado todo el directorio comps dentro de src/comps/

```
py_freecad/              # python scripts for FreeCAD
  +-- comps/               # library of components
      +-- .git/               # carpeta del repositorio git
      +-- comps.py            # components
      +-- kcomp.py            # constants about components
      +-- fcfun.py            # library of functions
      +-- ....
  +-- mi_pyfcad/
      +-- .git/               # carpeta del repositorio git
      +-- src/
          +--prueba.py        # este fichero usa funciones de ../../comps
          +-- comps/          # esta es copia del repositorio comps
              +-- comps.py            # components
              +-- kcomp.py            # constants about components
              +-- fcfun.py            # library of functions
              +-- ....
```

Con esto se ha copiado/comprimido (squashed) toda la historia del comps en `mi_pyfcad`

Si quisiese utilizar los ficheros del comps locales, dentro de mi repositorio, debería cambiar el camino (path) en nuestro fichero `prueba.py`:

```
sys.path.append(filepath + '/' + 'comps'
```

Con esto, ya podemos hacer los cambios que hagamos en `comps` local dentro de `mi_pyfcad`

Para actualizar cambios futuros, no se hace `subtree add`, sino `subtree pull`. Sin embargo, es mejor primero hacer commit de todos los cambios de este directorio y luego añadir los cambios del comps
```
py_freecad/mi_pyfcad (master) $ git subtree pull --squash --prefix=src/comps/ comps master
```

