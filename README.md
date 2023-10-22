# keeb
keyboard sharing client and server

These scripts redirect keystrokes from one computer to another. The server is the computer that has the keyboard, and the client is the computer that receives the keystrokes. 

## Potential features

- on the fly macros
- 

## Message format

|mtype|data|
|---|---|
|0|keyup
|1| keydown
|2| keyhold
|3|keepalive
|4| change target (sender only)
|5| quit


## __serve.py__

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
    lt
end

subgraph "keepalive"
    ka
end

subgraph "send"
    st
end

subgraph "media keys"
    gk2("getkeys()")
end
gk2 --> qoo


```


## __linuxClient.py__

```mermaid
graph LR
rcv("recvthings()")
pk("pushkeys()")

qin(qin)

rcv --> qin --> pk

subgraph "receive process"
    rcv
end


```

