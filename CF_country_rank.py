import urllib
import urllib.request
import sys, getopt


countryName = "Bangladesh"
countryRankList = []
rowHeader = "<tr participantId"
rowFooter = "Points in Normal Time"
handleHeader = "profile/"
rankHeader = "<td>"
rankFooter = "</td>"
nameHeader = '<div style="font-size: 0.8em; color: #777;">'
nameFooter = ","
instituteHeader = "organization/"
instituteSubHeader = ">"
instituteFooter = "<"


def getData(rowData):
    idx = 0
    temp = ""
    handle = ""
    rank = ""
    while idx < len(rowData):
        temp += rowData[idx]
        idx = idx + 1
        if temp.find(rankHeader) != -1:
            temp = ""
            break
    while idx < len(rowData):
        if rowData[idx] >= "0" and rowData[idx] <= "9":
            rank += rowData[idx]
        temp += rowData[idx]
        idx = idx + 1
        if temp.find(rankFooter) != -1:
            temp = ""
            break
    while idx < len(rowData):
        temp += rowData[idx]
        idx = idx + 1
        if temp.find(handleHeader) != -1:
            break
    while idx < len(rowData):
        if rowData[idx] == '"':
            break
        handle += rowData[idx]
        idx = idx + 1
    return rank, handle


def getTopGuy(httpResponse):
    idx = 0
    temp = ""
    topRow = ""
    while idx < len(httpResponse):
        temp += httpResponse[idx]
        idx = idx + 1
        if temp.find(rowHeader) != -1:
            temp = ""
            break
    while idx < len(httpResponse):
        topRow += httpResponse[idx]
        idx = idx + 1
        if topRow.find(rowFooter) != -1:
            break
    rank, handle = getData(topRow)
    return handle


def parsePage(httpResponse):
    idx = 0
    temp = ""
    isInsideRow = False
    while idx < len(httpResponse):
        temp += httpResponse[idx]
        idx = idx + 1
        if isInsideRow == False:
            if temp.find(rowHeader) != -1:
                temp = ""
                isInsideRow = True
        else:
            if temp.find(rowFooter) != -1:
                if temp.find(countryName) != -1:
                    countryRankList.append(getData(temp))
                temp = ""
                isInsideRow = False


def getName(httpResponse):
    idx = 0
    temp = ""
    name = ""
    while idx < len(httpResponse):
        temp += httpResponse[idx]
        idx = idx + 1
        if temp.find(nameHeader) != -1:
            if httpResponse[idx] == "<":
                return ""
            break
    temp = ""
    while idx < len(httpResponse):
        temp += httpResponse[idx]
        if temp.find(nameFooter) != -1:
            break
        name += httpResponse[idx]
        idx = idx + 1
    return name


def getInstitute(httpResponse):
    idx = 0
    temp = ""
    institute = ""
    while idx < len(httpResponse):
        temp += httpResponse[idx]
        idx = idx + 1
        if temp.find(instituteHeader) != -1:
            break
    temp = ""
    while idx < len(httpResponse):
        temp += httpResponse[idx]
        idx = idx + 1
        if temp.find(instituteSubHeader) != -1:
            break
    temp = ""
    while idx < len(httpResponse):
        temp += httpResponse[idx]
        if temp.find(instituteFooter) != -1:
            break
        institute += httpResponse[idx]
        idx = idx + 1
    return institute


def getInfo(handle):
    name = ""
    institute = ""
    url = "https://codeforces.com/profile/" + handle
    httpResponse = str(urllib.request.urlopen(url).read())
    name = getName(httpResponse)
    institute = getInstitute(httpResponse)
    if len(name) != 0 and len(institute) != 0:
        return " (" + name + "), " + institute
    elif len(name) != 0:
        return " (" + name + ")"
    elif len(institute) != 0:
        return ", " + institute
    else:
        return ""


def parseContest(contestId):
    rootUrl = "https://codeforces.com/contest/" + str(contestId) + "/standings/page/"
    lastTopGuy = ""
    pageIdx = 0
    while True:
        pageIdx = pageIdx + 1
        url = rootUrl + str(pageIdx)
        httpResponse = str(urllib.request.urlopen(url).read())
        currentTopGuy = getTopGuy(httpResponse)
        if currentTopGuy == lastTopGuy:
            break
        lastTopGuy = currentTopGuy
        print("parsing page " + str(pageIdx) + "...")
        parsePage(httpResponse)
        print(
            str(pageIdx)
            + " parsed. ranklist length so far: "
            + str(len(countryRankList))
        )
        if len(countryRankList) >= 5:
            break
    print("done\n")
    limit = min(10, len(countryRankList))
    print("Top " + str(limit) + " Ranks for Bangladesh in contest " + str(contestId))
    for i in range(limit):
        rank, handle = countryRankList[i]
        countryRow = str(i + 1) + ": (" + rank + ") " + handle + getInfo(handle)
        print(countryRow)


def main(argv):
    contestID = 0
    try:
        opts, args = getopt.getopt(argv, "hi:c:", ["contest_id=", "country_name="])
    except getopt.GetoptError as exc:
        print(str(exc))
        print("Usage: python3 CF_country_rank.py -i <contest_id> -c <country_name>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("python3 CF_country_rank.py -i <contest_id> -c <country_name>")
            sys.exit()
        elif opt in ("-i", "--contest_id"):
            contestID = arg
        elif opt in ("-c", "--country_name"):
            countryName = arg

    parseContest(contestID)


if __name__ == "__main__":
    main(sys.argv[1:])
