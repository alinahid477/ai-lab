

```
export $(grep -v '^#' .env | xargs)
uvicorn server:app --reload
```