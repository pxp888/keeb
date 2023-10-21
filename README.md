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


subgraph "keepalive process"
    ka
end

subgraph "send process"
    st
end


```


### __linuxClient.py__

```mermaid
graph LR
rcv("recvthings()")
pk("pushkeys()")
mm("moveMous()")
qin(qin)

rcv --> qin --> pk
rcv --> qoo --> mm


subgraph "receive process"
    rcv
end

subgraph "mouse process"
    mm
end

```

