#!/usr/bin/env python
#coding=utf-8

import web
import curricular
from bs4 import BeautifulSoup

urls=(
        "/","index",
        "/table","table"
        )
app=web.application(urls,globals())

class index:
    def GET(self):
        render=web.template.render("templates")
        bs1=curricular.getopener()[2]
        choicelist=[]
        for i in bs1.findAll('option'):
            choicelist.append(i.string)
        print choicelist
        if web.input().get("set") is not None:
            return render.index(choicelist,True)
        else:
            return render.index(choicelist,False)

class table:
    def POST(self):
        render=web.template.render("templates")
        No=web.input().get("No")
        year=web.input().get("year")
        bs1=curricular.getTable(a=No,y=year)
        if bs1 is None:
            raise web.seeother("/?set=1")
        tab=curricular.getTimetable(bs1)
        stuinfo=curricular.getStuinfo(bs1)
        classes,total=curricular.getClasses(bs1)
        return render.table(tab,stuinfo,total,classes)


if __name__=="__main__":
    app.run()

