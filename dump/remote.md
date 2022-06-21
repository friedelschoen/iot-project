# PROTOCOL REMOTE CLIENT

> Serial USB met 115200 baud!

**Stuurt JSON-objecten met een newline als terminator**

- **een request bevat altijd de string `'command'` ([see commands](#commands))**
- **een response bevat altijd de string `'error'` ([see errors](#errors))**

## Commands

### `hello`

> initialiseert de connectie

```
→ { "command": "hello" }
← { "error": null }
```
---

### `connect host=<string> port=<int>`

> opend een remote http-client ipv. de 5g-module

```
→ { "command": "connect", "host": "muizenval.tk", "port": 8080 }
← { "error": null }
```
---

### `send method=<string> endpoint=<string> headers?=<object> body?=<any>`

&rarr; `code=<int> headers=<object> body=<any>`
> stuurt een http-request naar de server

```
→ { "command": "send", "method": "POST", "endpoint": "/api/update", "headers": {}, "body": { "latitude": 53.2414306640625, "longitude": 6.533237711588542, "accuracy": 58.479530859171305, "battery": 394, "temperature": 25 } }
← { "error": null, "code": 200, "headers": { "Content-Type": "application/json" }, "body": {} }
```
---

## Errors

| code				| description									|
| ----------------- | --------------------------------------------- |
| `null`			| succes 										|
| `'invalid-json'`	| request is verkeerd geformateerd 				|
| `'not-available'`	| geen connectie naar de server mogelijk 		|
| `'not-connected'`	| request verstuurd zonder geconnect te zijn 	|