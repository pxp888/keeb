# keeb
keyboard sharing client and server

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

subgraph "main thread"
    gk
    ka
    lt
    qoo
end

subgraph "send thread"
    st
end

```
