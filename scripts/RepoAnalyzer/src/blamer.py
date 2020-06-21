import subprocess
import sys

gitDirectory = sys.argv[1].strip()
sourceDirectory = gitDirectory[:-4] #Drops the /.git
assetDirectory = sys.argv[2].strip()
theBranch = sys.argv[3].strip()
print("ALL ARGUMENTS ARE ... ", sys.argv)
#Returns a set of line numbers if there is at least one non-whitespace, non-comment char
def nonCommentLines(fName):
    nonComs = set()
    with open(fName, encoding="utf8", errors='ignore') as f:
        lines = f.read().splitlines()
        lineNo = 1
        inBlockComment = False
        for line in lines:
            line = line.strip()
            if not line.find('//') == 0:
                if line.find("/*") != -1:
                    inBlockComment = True                
                if not inBlockComment and len(line) > 0:
                    nonComs.add(lineNo)
                if inBlockComment and line.find("*/") != -1:
                    inBlockComment = False
            lineNo += 1
    return nonComs
    

with open(assetDirectory + 'changes.txt') as f:
    lines = f.read().splitlines()
    lines = [x.split(",") for x in lines]

currentRepo = "NOT_SET"
blameFilePath = assetDirectory + "blames.txt"
blameFile = open(blameFilePath,"w") 
##prefix = "C:\\Projects\\Thesis\\Staging\\"
#gitLocation = prefix + "\\.git"
#Set the current branch to master or trunk
# out = subprocess.call("git --git-dir=" + gitLocation + " checkout master", shell=True)
#"git --git-dir=" + gitDirectory + " --work-tree=" + sourceDirectory + " checkout -f master"

out = subprocess.call("git --git-dir=" + gitDirectory + " --work-tree=" + sourceDirectory + " checkout -f " + theBranch, shell=True)
if(out != 0):
    print("FAILED TO CHECKOUT COMMIT MASTER")
    exit()
totalRuns = len(lines)
currentRun = 0
for entry in lines:
    print("RUN: " + str(currentRun) + " / " + str(totalRuns))
    currentRun+=1
    repo = entry[0]
    theFile = entry[1]
    lineStart = int(entry[2])
    lineNumbers = int(entry[3])
    ticketId = entry[4]
    #Need to checkout the correct commit if not 
    if repo != currentRepo:
        out = subprocess.call("git --git-dir=" + gitDirectory + " --work-tree=" + sourceDirectory + " checkout -f " + repo, shell=True)
        currentRepo = repo
        if(out != 0):
            print("FAILED TO CHECKOUT COMMIT " + repo)
            exit()
    #OK AT THIS POINT WE ARE IN THE CORRECT COMMIT
    #We need to get the outputs of the git blame
    # command = "git --git-dir=" + gitLocation + " blame " + theFile + " -L" + str(lineStart) + "," + str(lineStart + lineNumbers - 1)
    command = "git --git-dir=" + gitDirectory + " --work-tree=" + sourceDirectory + " blame " + sourceDirectory + theFile + " -L" + str(lineStart) + "," + str(lineStart + lineNumbers - 1)
    out = subprocess.check_output(command , shell=True)    # print(repo + " " + theFile + " " + str(lineStart) + " " + str(lineNumbers) + " " + ticketId)
    out = out.decode("utf-8", "ignore")
    outputLines = out.strip().split("\n")
    badCommits = set()
    nonComLines = nonCommentLines(sourceDirectory + theFile)
    for outLine in outputLines : 
        if lineStart in nonComLines:
            outLine = outLine.strip()
            if len(outLine) == 0:
                pass
            blameCommit = outLine.split()[0].strip()                
            badCommits.add(blameCommit)
        lineStart += 1
    for blameCommit in badCommits:
        blameCommit = subprocess.check_output("git --git-dir=" + gitDirectory + " rev-parse " + blameCommit , shell=True) #Turn short commit into long commit
        blameCommit = blameCommit.decode("utf-8", "ignore").strip()
        blameFile.write(blameCommit + " " + theFile + " " + ticketId + "\n")
    print("|||")
    print(outputLines)
    print("|||")
blameFile.close()
out = subprocess.call("git --git-dir=" + gitDirectory + " --work-tree=" + sourceDirectory + " checkout -f " + theBranch, shell=True)
if(out != 0):
    print("Failed to checkout file! to", sourceDirectory)
    print("git --git-dir=" + gitDirectory + " checkout -f " + hashId + ' ' + sourceDirectory)
    exit()
# print(lines)
