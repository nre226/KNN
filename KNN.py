import csv
import math
import random
import copy
import ast

#getData is used for reading in the base.base dataset and creating a dictionary containing a list of tuples under each key as the output

def formatData():
    datadict = {}
    onecount = 0
    twocount = 0
    threecount = 0
    fourcount = 0
    done = False
    choices = []
    it = 0
    with open('u1-base.base', 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        while (done == False):
            choice = random.randint(1, 4)
            if (choice == 1 and onecount < 20000):
                onecount = onecount + 1
                choices.append(1)
            if (choice == 2 and twocount < 20000):
                twocount = twocount + 1
                choices.append(2)
            if (choice == 3 and threecount < 20000):
                threecount = threecount + 1
                choices.append(3)
            if (choice == 4 and fourcount < 20000):
                fourcount = fourcount + 1
                choices.append(4)
            if (onecount == 20000 and twocount == 20000 and threecount == 20000 and fourcount == 20000):
                done = True
        for row in reader: #read each row
            row = row[:-1] #slice off the time stamp
            for i in range(len(row)): #for each row
                row[i] = int(row[i]) # make the row an int
            choice = random.randint(1,4)
            tup = (row[1], row[2], choices[it])
            if(row[0] in datadict):
                datadict[row[0]].append(tup)
            else:
                datadict[row[0]] = []
                datadict[row[0]].append(tup)
            it = it + 1
        return datadict


def saveData(datadict, datafile):
    w = csv.writer(open(datafile, "w"))
    for key, val in datadict.items():
        w.writerow([key, val])

def getData():
    datadict = {}
    with open('saveddata.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if(row == []):
                continue
            row[0] = int(row[0])
            row[1] = ast.literal_eval(row[1])
            datadict[row[0]] = row[1]
    return datadict


#calcDist was used at the beginning steps of the program to find the distances
#After the initial running of calcDist the distances list was saved and loaded for each running

def calcDist(datadict):
    distances = []
    for i in range(1, len(datadict)+1): #look at the dict entry, want to look one ahead for the next comparision
        currlst = []
        for t in range(i+1, len(datadict)+1, 1):#look at the next key entry in the dict
            topsum = 0
            bottomleft = 0
            bottomright = 0
            bottomleftlst = []
            bottomrightlst = []
            for j in range(len(datadict[i])): #for the values in the i part
                for k in range(len(datadict[t])): #for the values in the next part
                    if(datadict[i][j][0] == datadict[t][k][0]): #if they have the same films
                        curr = datadict[i][j][1]*datadict[t][k][1] #do the cosine comp.
                        topsum = topsum+curr
                        bottomleftlst.append(datadict[i][j][1])
                        bottomrightlst.append(datadict[t][k][1])
            for a in range(len(bottomleftlst)):
                curr = bottomleftlst[a]*bottomleftlst[a]
                bottomleft = bottomleft + curr
            bottomleft = math.sqrt(bottomleft)

            for b in range(len(bottomrightlst)):
                curr = bottomrightlst[b]*bottomrightlst[b]
                bottomright = bottomright + curr
            bottomright = math.sqrt(bottomright)

            if(topsum != 0):
                currdist = (topsum)/(bottomleft*bottomright)
            else:
                currdist = 0
            currlst.append(currdist)
        distances.append(currlst)

    return distances


#Similar to calcDist was used to write the distances list to a file.
def writeDist(distances, distancefile):
    newfile = open(distancefile, 'w')
    for item in distances:
        newfile.write("%s\n" % item)
    newfile.close()

#opens the dist.txt file and reads/correctly formats the distance list that was calculated above
def getDist(filename):
    distances = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            currlst = []
            if(len(row) == 1):
                entry = row[0][1:][:-1]
                row.pop(0)
                row = [entry] + row
            else:
                begin = row[0][1:]
                end = row[-1][:-1]
                row = row[:-1]
                row.pop(0)
                row = [begin]+row
                row.append(end)
            for val in row:
                val = float(val)
                currlst.append(val)
            distances.append(currlst)
    return distances


def NN(userid, movieid, datadict, distances, k):
    potentials = []
    targetdist = []
    totalrating = 0
    for i in datadict:
        for j in range(len(datadict[i])):
            if(datadict[i][j][0] == movieid and i>userid):
                potentials.append(i)
    for target in potentials:
        currdist = distances[userid-1][target-userid-1]
        val = (target, currdist)
        targetdist.append(val)
    targetdist.sort(key=lambda x: x[1])
    targetdist = targetdist[-k:]
    for j in range(len(targetdist)):
        curr = targetdist[j][0]
        for h in range(len(datadict[curr])):
            if(datadict[curr][h][0] == movieid):
                rating = datadict[curr][h][1]
                break
        totalrating = totalrating + rating
    totalrating = totalrating/k
    return totalrating


def getActual():
    datadict = {}
    with open('u1-test.test', 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:  # read each row
            row = row[:-1]  # slice off the time stamp
            for i in range(len(row)):  # for each row
                if(i==2):
                    row[i] = float(row[i])
                else:
                    row[i] = int(row[i])  # make the row an int
            tup = (row[1], row[2])
            if (row[0] in datadict):
                datadict[row[0]].append(tup)
            else:
                datadict[row[0]] = []
                datadict[row[0]].append(tup)
        return datadict

def findTotalError(actualdict, datadict, distances, k):
    errorsum = 0
    count = 0
    for i in actualdict:
        for j in range(len(actualdict[i])):
            count = count + 1
            userid = i
            movieid = actualdict[i][j][0]
            result = NN(userid, movieid, datadict, distances, k)
            actual = actualdict[i][j][1]
            error = (result - actual) * (result - actual)
            errorsum = errorsum + error
    totalerror = errorsum / count
    return totalerror

#using 4-fold cross validation to determine the best K value for KNN
def foldit(datadict, k):
    orgdata = copy.deepcopy(datadict)
    totalerror = 0
    for a in range(1,5,1):
        print('loop')
        datadict = copy.deepcopy(orgdata)
        bin = {}
        for i in datadict: # bin all the data according to the folds
            j = 0
            while j < len(datadict[i]):
                if(datadict[i][j][2] == a):
                    if(i in bin):
                        bin[i].append(datadict[i][j])
                        del datadict[i][j]
                        j = j-1
                    else:
                        bin[i] = []
                        bin[i].append(datadict[i][j])
                        del datadict[i][j]
                        j = j-1
                j = j+1
        if(a == 1):
            distances = getDist('fold1dist.txt')
        if(a == 2):
            distances = getDist('fold2dist.txt')
        if(a == 3):
            distances = getDist('fold3dist.txt')
        if(a==4):
            distances = getDist('fold4dist.txt')
        print('got the distance loaded')
        error = findTotalError(bin, datadict, distances, k)
        print('error', a, 'done')
        totalerror = totalerror+error
    totalerror = totalerror/4
    return totalerror


def main():
    distancefile = 'dist.txt'
    #datadict = formatData()
    #saveData(datadict, 'saveddata.csv')
    datadict = getData()
    # actualdict = getActual()
    # distances = calcDist(datadict)
    # writeDist(distances, distancefile)
    # distances = getDist('dist.txt')
    # totalerror = findTotalError(actualdict, datadict, distances, 3)
    # print("The base datasets total error is:", totalerror)
    k2error = foldit(datadict,2)
    print("The K2 error is", k2error)
    k4error = foldit(datadict,4)
    print("The K4 error is", k4error)
    k6error = foldit(datadict, 6)
    print("The K6 error is", k6error)
    k8error = foldit(datadict, 8)
    print("The K8 error is", k8error)
    k10error = foldit(datadict, 10)
    print("The K10 error is", k10error)

main()