# Troubleshooting

## FileNotFoundError

When running `capstone` you may receive a `FileNotFoundError` in the data loading and cleaning phase. Efforts are underway to solve this bug. In the meantime, you can try to unhash your `capstone command`

```bash
unhash capstone
capstone
```

If the problem persists, please verify the capstone project is not installed globally and run again.
