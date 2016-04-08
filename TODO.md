# TODO & Milestones

## Until 2.1 - Init

* [ ] create the core-, devices-, and services-modules
* [ ] create a CLI-interface (separate Repo?)
    * [x] must be able to detect whether an instance of SAM is already running on a server
    * [ ] connect to existing instance, if available
    * [ ] start new instance if not
    * [ ] insert elements into the core's input queue
    * [ ] read and remove elements from the core's output queue
    * [ ] Comments, Explanations for the user
* [ ] create the context module

## until 2.2 - Automation

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
