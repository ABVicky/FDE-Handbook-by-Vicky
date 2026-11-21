# Exercise 04 — Map the network

1. What is your laptop's **private** IP address? (macOS: `ipconfig getifaddr en0`; Linux/WSL: `hostname -I` or `ip addr`.) Which private range from Lesson 05 is it in?
2. Look up the IP addresses of `example.com`, `github.com` and `api.github.com` with `dig +short` (or `nslookup`). Do any return more than one address? Why might a site do that?
3. Look up a name that doesn't exist, e.g. `this-name-does-not-exist-fde.example`. What does the tool say?
4. List every program **listening** on a TCP port on your machine. Pick two and find out what they are.
5. Start `python3 -m http.server 8000`, then try to start a **second** one on port 8000 in another terminal. What error do you get? How would you find which process already owns the port?
6. Use `nc -vz example.com 443` and `nc -vz example.com 81` (add `-w 5` to limit the wait to 5 seconds). What's the difference in the results, and what does each tell you?

## Draw it

7. Draw (on paper or in Mermaid) the path a request takes from your laptop to `example.com`: your laptop, router, DNS lookup, the internet, the server. Label the IP and port at each end.
