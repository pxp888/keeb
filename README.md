# keeb
keyboard sharing client and server


|mtype|data|
|---|---|
|0|keyup
|1| keydown
|2| keyhold
|3|keepalive
|4| change target (sender only)
|5| quit
|6| toggle scroll


### __serve.py__

```mermaid
graph LR

gk("getkeys()")
ka("keepalive()")
qoo(qoo)
st("sendthings()")
lt("localtype()")


gk & ka --> qoo --> st
gk --> lt
st --> x & y

```

### __client.py__

```mermaid
graph LR
rcv("recvthings()")
pk("pushkeys()")

rcv --> pk
```

