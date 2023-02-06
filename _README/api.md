
### Interface

There are four endpoints with seven supported method calls altogether
```
op        uri            methods
---------------------------------------------------------
list      /              get     post    
detail    /id/           get             patch     delete
notify    /id/notify             post
logs      /id/log        get
```

#### Auth

Access varies by three user classes - staff, registered, and temporary token access
```
op        uri            method:auth*
---------------------------------------------------------
list      /              get:r*  post:r
detail    /id/           get:t           patch:t   delete:s
notify    /id/notify             post:t
logs      /id/log        get:r*

* t: unregistered event party with token; r: registered user, *party-to events; s: staff

```


#### OpenAPI

See [_m/openapi-schama.yaml](_m/openapi-schema.yaml)
or run
```./manage.py generateschema```
or visit ```$host/openapi```

```
$path/ vs $path  dj/humyn vs api/machine
```

