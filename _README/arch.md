
### Architecture, design, process



```
....|....1....|....2....|....3....|....4....|....5....|....6....|....7....|....8....|....9....|....0
```

The core entity is the Event class
```
event
  parties   user | anon
  slots     [ begin, duration ]
  title     optional string
  log       [ entries ]
```
- Inclusion of non-registered email creates an inactive user record
- Party/user list cannot be altered after event creation
- Time slot list can be narrowed or extended indefinitely
- A gibberish title is generated if one is not provided
- Creation, update, related notification, and deletion are logged in detail


An Event has three main relations, to user/parties, time slots, and log entries
```
            event                         
              parties >---< user
slot >------- slots           email 
  begin       title                          
  duration    log --------< entry           
                              when          
                              occurrence    
                              effector      
                              slots         
                              data
```
- ```User``` is a relation to Django/AUTH_USER_MODEL, relying only on email address
- The ```begin``` field of a ```slot``` is a normal timezone-aware Django db field
- Log ```entry``` is a flat structure[, so there are no second order relations]
- The ```slots``` field of a log ```entry``` is thus fixed size, which places a limit on the number of slots
- The ```data``` field of a log ```entry``` stores indication of token usage, notification recipient, and/or event open/close actions as applicable


An EmailToken is created and sent with notifications for non-authenticated access
```
emailtoken
  event >--- event
  user >---- user
  key
  expires
```
Expiration defaults to five days, or the value of EMAILTOKEN_EXPIRATION_DAYS setting


#### Design
```
disinterleaving
naming splay  splay:join
complexities  auth  tok  log
awareness enhancing  design  practice  strategem

axials:
fixed parties : avoid confusion : log clarity ; reset op: copy slots title, close

```
```
career: 
...
```

##### Cases
```
groupings:
- storage, close/delete net, confirm, update flow
- left to you cases - realistically, overlays on spec

closed : slots [] or [1] + confirmation
delete reserved  only log of closing  future maint op

confirm: view=  not req  updy same
confirm : view vs update  all vs all-1

expected flow  reopen by copying title  prevserved in log  id is pk

- ewe eye  mechane
- lamport/vector test
- beeptime net
- machine <-> machine

aspects:
soa dj drf  eval study integrate
net time
sec contain
wrkflow tooling

```
- 


##### Security

The project aims to be small, coherent, and auditable.
```
- no incentive, eml/dt and evt title only
- disposability
- no disaster case
- PII cases, pwd reuse cases

core axials ?
log authn/z pii disposabil

..roles?
sender initiator
recipient token
staff super
[mailhost]
```

##### Mail / notifications

```
- sendmail, localnet
- _ mailhog

agnostic on agree/confirm operation process
mail  sms  talk
m/t q
myriad svc net
celery redis kafka  broker queue


req slots to match latest
  no mis-notification
   ?error means
```

##### Time

...
```
ISO 8601
RFC 3339
https://stackoverflow.com/questions/522251/whats-the-difference-between-iso-8601-and-rfc-3339-date-formats
[RFC 2822]

CSP papers 1,2,3  hickey
```
<!-- tba ftw -->

##### Validation

```
post
patch
notify
delete
```
<!--
list      /              get     post    
detail    /id/           get             patch     delete
notify    /id/notify             post
logs      /id/log        get
-->

##### Logs

```
event
parties
entries
  id
  when
  occurrence : update | notify | view
  effector : user
  slots
  data : { token, opened, closed, recipient }
```

##### Documentation

- [grip/fork] / rdmd
- @todo: docstrings

<!-- @todo
##### Extensibility
-
-
-->

##### Motivations
```
minima complexity

career / tech path

- no (g)ui  dj api  diag ver  test design  audit trail  containeren
- coherent (pythonic) subset of posix sh .. refining
small scale code/arch/test/etc view tools
sh -> py underview
    py wraps unix/posix

network experiments
```
#### Process
```
gluing together
sense of flow
layer
deriv
strategy
debug/diag / exper process
  work loop
pdb / test loop
    reinventing sh

act
lzydkr
grip
apifuz

```



#### Stats

##### tree

```
%[tree]
```

##### cloc

```
%[cloc]

https://github.com/AlDanial/cloc
```

##### wc
```
%[wc]
```



