import copy

def next_gen(cells):
    size_x  = len(cells)
    size_y  = len(cells[0])

    addlist = []

    returnable = copy.deepcopy(cells)

    anothercopy = copy.deepcopy(cells)
    
    for c in range(size_y):
        addlist.append(0)
        
    cells.insert(0, addlist)

    addlist2 = copy.deepcopy(addlist)
    
    cells.append(addlist2)
    
    for list2 in cells:
        print('before:', list2)
        list2.insert(0, 0)
        list2.append(0)
        print('after:', list2)
        
    print(cells)


    xxindex = 1
    yyindex = 1
    
    for xx in cells[1:-1]:
        yyindex = 1
        for yy in xx[1:-1]:
            alive_nbs = 0
            for x in range(xxindex - 1, xxindex + 2):
                for y in range(yyindex - 1, yyindex + 2):
                    if cells[x][y] == 1:
                        if x != xxindex or y != yyindex:
                            alive_nbs += 1

            if alive_nbs == 3:
                returnable[xxindex - 1][yyindex - 1] = 1
                state = 'alive'
            else:
                returnable[xxindex - 1][yyindex - 1] = 0
                state = 'dead'
                
            print('[{0}] [{1}] : {2}\n'.format(str(xxindex), str(yyindex), state))
            yyindex += 1
        xxindex += 1

    print(str(anothercopy).replace('],', ']\n').replace('1', 'x').replace('0', 'o').replace(',', '') + '\n')
    return returnable

cls = [[0,1,1,0,1],[0,0,1,1,0],[0,1,1,0,1],[1,1,1,1,0],[0,0,0,0,0]]
print(str(next_gen(cls)).replace('],', ']\n').replace('1', 'x').replace('0', 'o').replace(',', ''))
