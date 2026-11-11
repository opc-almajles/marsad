#!/usr/bin/env python3
"""Build feed.xml (RSS 2.0) from data.json for the SharePoint sync flow.
Each <item>: <title> = record id, <description> = JSON body ready for the
SharePoint REST API (list «مرصد الفرص», internal field names). Run from the repo root."""
import json, datetime as D
from xml.sax.saxutils import escape
PATH = {"فعالية": "حضور", "تحدث": "مشارك"}
d = json.load(open("data.json", encoding="utf-8"))
def dt(v): return (v + "T00:00:00+04:00") if v else None
def url(v): return {"Url": v, "Description": v[:250]} if v else None
items = []
now = D.datetime.now(D.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
for r in d["opps"]:
    doms = r.get("domains") or ([r["domain"]] if r.get("domain") else [])
    body = {
        "Title": r.get("title") or "", "Organizer": r.get("organizer"),
        "EntityType": r.get("etype"), "Emirate": r.get("emirate"),
        "MainDomain": doms[0] if doms else None, "Domains": doms,
        "Path": PATH.get(r.get("path"), r.get("path")), "OppType": r.get("type"),
        "StartDate": dt(r.get("start")), "EndDate": dt(r.get("end")), "Deadline": dt(r.get("deadline")),
        "Status": r.get("status"), "Verification": r.get("verify"),
        "AwardKinds": r.get("awardKind") or [], "AwardWindow": r.get("window"),
        "OfficialURL": url(r.get("orgUrl")), "SourceURL": url(r.get("url")),
        "LastChecked": dt(r.get("checked")), "RecordID": r["_id"],
    }
    items.append("<item><title>%s</title><guid isPermaLink=\"false\">%s-%s</guid><link>https://opc-almajles.github.io/marsad/#%s</link><pubDate>%s</pubDate><description><![CDATA[%s]]></description></item>" % (
        escape(r["_id"]), escape(r["_id"]), d.get("updated", ""), escape(r["_id"]), now,
        json.dumps(body, ensure_ascii=False).replace("]]>", "]]&gt;")))
xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>مرصد الفرص – مزامنة</title>'
       '<link>https://opc-almajles.github.io/marsad/</link><description>Sync feed for SharePoint</description>'
       '<lastBuildDate>%s</lastBuildDate>\n%s\n</channel></rss>\n') % (now, "\n".join(items))
open("feed.xml", "w", encoding="utf-8").write(xml)
print(len(items), "items")
