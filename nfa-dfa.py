class Automata:#유한 오토마타 클래스
    def __init__(self,a=[],b=[],c={},d="default",e=[]):
        self.stateSet=a
        self.terminalSet=b
        self.deltaFuncs=c#델타함수는 딕셔너리 자료형 사용
        self.startState=d
        self.finalStateSet=e

    def printFA(self):#오토마타 정보 출력
        print("state set : ", self.stateSet)
        print("terminal set : ", self.terminalSet)
        print("delta functions : ", self.deltaFuncs)
        print("start state : ", self.startState)
        print("final state set : ", self.finalStateSet)
        
    def closure(self, a):#상태 튜플 a 의 epsilon-closure 튜플 반환
        epsilon_closure=list(a)
        temp = []
        for state in epsilon_closure:
            if (state, 'ε') not in self.deltaFuncs:
                continue#입실론을 보고 갈 수 있는 상태가 없다면 넘어가기
            temp.extend(self.deltaFuncs[(state,'ε')])#입실론을 보고 갈 수 있는 상태를 temp에 추가
            for tempState in temp:
                if tempState not in epsilon_closure:#temp에 추가된 상태가 결과(epsilon_closure)에 없는 상태면 추가
                    epsilon_closure.append(tempState)
        epsilon_closure.sort()#정렬
        return tuple(epsilon_closure)

def getNFA(n):#n번째 nfa 파일 읽어서 Automata 인스턴스 반환
    fileName="nfa"+str(n)+".txt"
    f=open(fileName, 'r', encoding='utf8')

    #stateSet 저장
    line=f.readline()
    stateSet=splitLine(line,2,1)
    
    #terminalSet 저장
    line=f.readline()
    terminalSet=splitLine(line,2,1)
    
    #deltaFuncs 저장
    line=f.readline()
    line=f.readline()#줄바꿈
    deltaFuncs={}
    while(line!='}\n'):
        state=line[1:5]
        symbol=line[7:8]
        result=splitLine(line,1,0)
        deltaFuncs[(state, symbol)]=result
        line=f.readline()
    
    #startState 저장
    line=f.readline()
    startState=line[13:17]
    
    #finalStateSet 저장
    line=f.readline()
    finalStateSet=splitLine(line,2,1)

    NFA=Automata(stateSet,terminalSet,deltaFuncs,startState,finalStateSet)
    return NFA
    f.close()

def splitLine(line, a, b):#nfa파일의 형식에 맞춰 {} 안의 값들만 빼서 리스트에 넣어서 반환
    start=line.find('{')
    end=line.find('}')
    vals=line[start+a:end-b].split(', ')#{}안에 띄어쓰기가 있는 경우를 고려해서 a,b로 범위조절
    return vals

def NFAtoDFA(nfa):#nfa를 dfa로 바꾸어 반환
    dfaStartState=nfa.closure((nfa.startState,))
    dfaStateSet=[dfaStartState]
    dfaTerminalSet=nfa.terminalSet
    dfaDeltaFuncs={}
    dfaFinalStateSet=[]
    for stateTuple in dfaStateSet:#dfa 상태집합의 튜플들 ('q000',)
        for symbol in nfa.terminalSet:#심볼들
            temp=[]
            for state in stateTuple:#튜플 내부의 진짜 상태들 'q000'            
                if(state,symbol) in nfa.deltaFuncs:#해당 상태에서 해당 심볼을 보고 갈 수 있는 델타함수가 존재할 때
                    temp.extend(nfa.deltaFuncs[(state, symbol)])
            if temp == []:#빈 집합이면 넘어가기
                continue
            temp=set(temp)#집합 자료형으로 바꿔서 중복 제거
            temp=list(temp)#다시 리스트로 변환
            temp.sort()#정렬
            temp=tuple(temp)#저장을 위해 상태들로 이루어진 튜플로 변환
            temp=nfa.closure(temp)#epsilon closure 해주기
            if temp not in dfaStateSet:
                dfaStateSet.append(temp)#새로운 상태 추가
            dfaDeltaFuncs[(stateTuple, symbol)]=temp#dfa의 델타함수 추가
    for stateTuple in dfaStateSet:
        for finalState in nfa.finalStateSet:
            if finalState in stateTuple and stateTuple not in dfaFinalStateSet:#nfa의 최종상태가 포함되고 최종 상태 집합에 없는 상태이면 추가
                dfaFinalStateSet.append(stateTuple)
    dfa = Automata(dfaStateSet, dfaTerminalSet, dfaDeltaFuncs, dfaStartState,dfaFinalStateSet)
    return dfa

def faStateSubst(dfa):#여러 상태를 하나의 상태로 치환((q000,q001)->q000)
    stateSubst={}#각 상태의 치환정보를 매핑
    newStateSet=[]
    newTerminalSet=dfa.terminalSet.copy()#터미널은 그대로
    newDelta={}
    newFinal=[]
    for i in range(len(dfa.stateSet)):
        stateName="q00"+str(i)#새로운 단일 상태 이름
        stateSubst[dfa.stateSet[i]]=stateName#기존 dfa상태와 새로운 단일 상태를 매핑
        newStateSet.append(stateName)#q000 형태의 단일 상태들만으로 이루어진 새로운 상태집합
    newStart=stateSubst[dfa.startState]
    for state in dfa.finalStateSet:#새로운 상태집합
        newFinal.append(stateSubst[state])
    for delta in dfa.deltaFuncs.keys():#새로운 델타함수
        newDelta[(stateSubst[delta[0]],delta[1])]=stateSubst[dfa.deltaFuncs[delta]]
    newDFA=Automata(newStateSet, newTerminalSet, newDelta, newStart, newFinal)
    return newDFA, stateSubst#새로운 dfa와 상태 치환 정보 반환
          
def reduceDFA(dfa):
    reducedStateSet=[dfa.finalStateSet]
    notFinal=dfa.stateSet.copy()#종결상태와 비종결상태로 분할
    for state in dfa.finalStateSet:
        notFinal.remove(state)
    reducedStateSet.append(notFinal)
    isReducible = True
    while isReducible:
        isReducible=False#분할가능한 상황을 만나지 않으면 종료
        stateCopy=reducedStateSet.copy()#분할 시 stateCopy를 분할하고 reducedStateSet에 복사
        indexList=[0 for i in range(len(dfa.stateSet))]
        for i in range(len(indexList)):#각 상태가 reducedStateSet에서 몇번째 그룹인지 저장
            state=dfa.stateSet[i]
            for j in range(len(reducedStateSet)):
                if state in reducedStateSet[j]:
                    indexList[i]=j
                    break
        
        for i in range(len(reducedStateSet)):
            if len(reducedStateSet[i])==1:#상태그룹에 상태가 하나밖에 없으면 분할 불가능
                continue
            outerResult=[]#상태그룹 안의 상태들이 각 심볼을 보고 어느 그룹으로 가는지를 저장
            for state in reducedStateSet[i]:
                innerResult=[]#심볼을 보고 어느 그룹으로 가는지 저장
                for symbol in dfa.terminalSet:
                    res=dfa.deltaFuncs.get((state,symbol))
                    if res==None:#해당 상태와 심볼에 대한 델타함수가 없으면 None으로 저장
                        innerResult.append(res)
                    else:
                        innerResult.append(indexList[dfa.stateSet.index(res)])
                outerResult.append(innerResult)
            partitionResult=[]#outerResult에서 중복을 제거
            for result in outerResult:
                if result not in partitionResult:
                    partitionResult.append(result)
            if(len(partitionResult)!=1):#중복을 제거한 결과의 크기가 1이 아니라면 분할 가능
                isReducible=True
                partition=[[] for group in partitionResult]#해당 상태그룹을 분할한 결과를 담을 리스트
                #outerResult 각각 읽어서 partitionResult 안의 몇번째 인덱스에 해당하는 그룹으로 갈건지 찾아서 partition의 해당 그룹에 append
                #다한 다음에 partition을 stateCopy에 extend하고 stateCopy 안에 잇는 분할하기 전 그룹 삭제
                for j in range(len(outerResult)):
                    partition[partitionResult.index(outerResult[j])].append(reducedStateSet[i][j])
                stateCopy.remove(reducedStateSet[i])#기존 그룹 삭제
                stateCopy.extend(partition)#분할한 그룹 추가
        reducedStateSet=stateCopy.copy()#reducedStateSet 업데이트
    reducedStateSet2=[tuple(state) for state in reducedStateSet]#형식 맞추기 위해 튜플 형식의 set 생성
    start=[]#reduced dfa의 start state
    for state in reducedStateSet:
        if dfa.startState in state:
            start=state#dfa의 시작상태가 있는 그룹을 reduced dfa의 시작상태로 지정
            break
    start=tuple(start)#튜플로 저장
    final=[]#종결상태
    for state in reducedStateSet:
        for dfaFinalState in dfa.finalStateSet:
            if dfaFinalState in state:#그룹 안에 종결상태가 있으면 추가
                final.append(state)
                break
    final2=[tuple(state) for state in final]
    terminal=dfa.terminalSet.copy()#터미널은 그대로
    delta={}
    for state in reducedStateSet:
        for symbol in terminal:
            res=dfa.deltaFuncs.get((state[0],symbol))#상태 묶음 안의 첫번째 원소를 골라 해당 원소가 어느 그룹으로 가는지 확인
            if res != None:
                for resultGroup in reducedStateSet:
                    if res in resultGroup:#결과가 들어있는 그룹 찾기
                        delta[(tuple(state),symbol)]=tuple(resultGroup)
                        break
    reducedDFA=Automata(reducedStateSet2, terminal, delta, start, final2)
    return reducedDFA

def writeResult(n):#n번째 입력파일에 대한 출력파일 생성
    fileName="nfa"+str(n)+"Result.txt"#nfa1Result.txt
    f=open(fileName, 'w', encoding='utf8')
    f.write('result for nfa'+str(n)+'.txt\n\n')#어느 파일에 대한 결과인지 명시
    nfa=getNFA(n)#nfa 불러오기
    outputs=[]#파일에 출력할 문자열들을 한줄씩 저장할 리스트
    outputs.append("---------------------------------------\n")
    outputs.append("step 1 : read (ε)-NFA from text file\n\n")#1단계
    outputs.append('(ε)-NFA : \n')

    stateSentence='StateSet = { '#상태집합
    for state in nfa.stateSet:
        stateSentence += (state+', ')
    stateSentence=stateSentence[:-2]#마지막 ', ' 제거
    stateSentence+=' }\n'
    outputs.append(stateSentence)

    terminalSentence='TerminalSet = { '#터미널집합
    for symbol in nfa.terminalSet:
        terminalSentence+=(symbol+', ')
    terminalSentence=terminalSentence[:-2]
    terminalSentence+=' }\n'
    outputs.append(terminalSentence)

    outputs.append('DeltaFunctions = {\n')#델타함수
    for key in nfa.deltaFuncs.keys():
        deltaLine='('+key[0]+', '+key[1]+') = {'
        for state in nfa.deltaFuncs[key]:
            deltaLine+=(state+', ')
        deltaLine=deltaLine[:-2]
        deltaLine+='}\n'
        outputs.append(deltaLine)
    outputs.append('}\n')

    outputs.append('StartState = '+nfa.startState+'\n')#시작상태

    finalSentence='FinalStateSet = { '#종결상태
    for state in nfa.finalStateSet:
        finalSentence += (state+', ')
    finalSentence=finalSentence[:-2]
    finalSentence+=' }\n\n'
    outputs.append(finalSentence)

    outputs.append("---------------------------------------\n")
    outputs.append("step 2 : convert NFA to DFA\n")#2단계
    dfa=NFAtoDFA(nfa)#nfa를 dfa로 변환
    dfa, sub1 = faStateSubst(dfa)#dfa의 상태를 단일상태로 치환하고 치환정보는 sub1에 저장
    outputs.append('\nstate substitution information : \n')#치환정보 출력
    sub=''#상태집합이 어떤 단일상태로 치환되는지 [q000]=q000, [q001, q002]=q001 ... 꼴로 출력
    for subInfo in sub1.items():
        sub+='['
        for state in subInfo[0]:
            sub+=(state+', ')
        sub=sub[:-2]
        sub+=(']->'+subInfo[1]+', ')
    sub=sub[:-2]
    outputs.append(sub+'\n\n')

    outputs.append('DFA : \n')
    stateSentence='StateSet = { '#상태집합
    for state in dfa.stateSet:
        stateSentence += (state+', ')
    stateSentence=stateSentence[:-2]
    stateSentence+=' }\n'
    outputs.append(stateSentence)

    terminalSentence='TerminalSet = { '#터미널집합
    for symbol in dfa.terminalSet:
        terminalSentence+=(symbol+', ')
    terminalSentence=terminalSentence[:-2]
    terminalSentence+=' }\n'
    outputs.append(terminalSentence)

    outputs.append('DeltaFunctions = {\n')#델타함수
    for key in dfa.deltaFuncs.keys():
        deltaLine='('+key[0]+', '+key[1]+') = {'+dfa.deltaFuncs[key]+'}\n'
        outputs.append(deltaLine)
    outputs.append('}\n')

    outputs.append('StartState = '+dfa.startState+'\n')#시작상태

    finalSentence='FinalStateSet = { '#종결상태
    for state in dfa.finalStateSet:
        finalSentence += (state+', ')
    finalSentence=finalSentence[:-2]
    finalSentence+=' }\n\n'
    outputs.append(finalSentence)

    outputs.append("---------------------------------------\n")
    outputs.append("step 3 : minimize DFA to reduced DFA\n")#3단계
    reducedDFA=reduceDFA(dfa)
    reducedDFA, sub2 = faStateSubst(reducedDFA)
    outputs.append('\nstate substitution information : \n')#치환정보 출력
    sub=''
    for subInfo in sub2.items():
        sub+='['
        for state in subInfo[0]:
            sub+=(state+', ')
        sub=sub[:-2]
        sub+=(']->'+subInfo[1]+', ')
    sub=sub[:-2]
    outputs.append(sub+'\n\n')

    outputs.append('reduced DFA : \n')
    stateSentence='StateSet = { '#상태집합
    for state in reducedDFA.stateSet:
        stateSentence += (state+', ')
    stateSentence=stateSentence[:-2]
    stateSentence+=' }\n'
    outputs.append(stateSentence)

    terminalSentence='TerminalSet = { '#터미널집합
    for symbol in reducedDFA.terminalSet:
        terminalSentence+=(symbol+', ')
    terminalSentence=terminalSentence[:-2]
    terminalSentence+=' }\n'
    outputs.append(terminalSentence)

    outputs.append('DeltaFunctions = {\n')#델타함수
    for key in reducedDFA.deltaFuncs.keys():
        deltaLine='('+key[0]+', '+key[1]+') = {'+reducedDFA.deltaFuncs[key]+'}\n'
        outputs.append(deltaLine)
    outputs.append('}\n')

    outputs.append('StartState = '+reducedDFA.startState+'\n')#시작상태

    finalSentence='FinalStateSet = { '#종결상태
    for state in reducedDFA.finalStateSet:
        finalSentence += (state+', ')
    finalSentence=finalSentence[:-2]
    finalSentence+=' }\n'
    outputs.append(finalSentence)

    for line in outputs:
        f.write(line)#저장된 문자열들을 파일에 출력
    f.close()
    print(fileName+' generated')


for i in range(10):#10개의 파일에 대해 입력, 변환, 출력
    writeResult(i+1)