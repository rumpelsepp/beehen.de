---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ now.Format "2006-01-02" }}
tags: []
# Titelbild für die Karte auf der Startseite und die Linkvorschau. Ohne
# Angabe wird feature.jpg aus diesem Ordner genommen, sonst ein Platzhalter.
# image: "feature.jpg"
toc: false
draft: true
---

Worum geht's? Ein, zwei Sätze als Einstieg.
{.lead}
