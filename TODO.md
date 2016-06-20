# TODO & Milestones

## Until 2.1 - Init

* [x] implement logging
* [ ] add missing docstrings
* [x] add a "web-interface" that allows reacting to messages sent over the web. Not flask this time - A simple listener on one port should be enough.
* [x] create the core-, devices-, and services-modules
* [x] create a CLI-interface to test stuff (-> separate Repo!)
* [ ] use _ to mark private stuff

## until 2.2 - Automation

* [ ] create the context module
* [ ] use decorators to subscribe to functions
* Rules

---

## At some point

* [ ] Setup
    * setup.py
    * requirements.txt
    * makefile?

> ```
> init:
>     pip install -r requirements.txt
>
> test:
>     py.test tests
> ```

* [ ] Tests that actually test something
