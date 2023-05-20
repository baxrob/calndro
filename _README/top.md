
![badge](https://github.com/baxrob/calndro/actions/workflows/ci.yml/badge.svg)


## An appointment coordination API

Contents: [scenario](#scenario) | [install](#install) | [api](#interface) | [tui](#tui) | [tests](#tests) | [design](#architecture-design-process) | [future](#next-possibly) | [ref](#ref)

---
<br>
<p align="center">
&mdash; <i>Document under &#128119; &#128679; &#128736;</i> &mdash;
</p>
<br>

This is a WIP POC. 
Briefly, its 
intent is similar to the core function of Calendly, or [cal.com](https://github.com/calcom/cal.com).
It's in an interim state with some cruft
at the edges,
but the 
main structure and operation are
relatively settled. 
<!--
an unneccessary experiment toward assurability
-->

In summary:
> Invite registered or unregistered parties, narrow to agreement on a scheduled time span, send notification of updates, with <!--all--> actions logged

```
propose -> narrow -> agree : audit
```

There's no graphical interface, but a [tui](#tui). 
The
[api](#interface)
is
small, with [somewhat and in the direction of] minimal corners.
[Install](#install) with venv/pip or docker.
[Tests](#tests)
may
give a 
simplest 
overview.
Below, 
you
can/may/will
find
some elaboration on
[design](#architecture-design-process)
process,
including some [stats](#stats)
and [workflow](#process) notes,
possible [future](#next-possibly)
expansion/s
and some
[background/contributing] /
[referential](#ref)
material.

<!-- X: s/<blockquote><i> -->
```
Note: draft text is marked with '@draft' in <code> or <details> blocks below
```
<!--
 [or cli?]
, or comments 
```
> Conventions used in this document:\\n\\n
> \s\s some pre/code blocks connote provisional notes

\\n
\n
```
-->


First a scenario



<!--
[scenario](#scenario)

[scenario](#scenario)
[install](#install)
[api](#interface)
[tui](#tui)
[tests](#tests)
[design](#architecture-design-process)
[future](#next-possibly)
[ref](#ref)
-->


