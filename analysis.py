import pathFind as pf
import populate_graph as pg
import networkx as nx
import csv
import random as rn
import sys

G = nx.DiGraph()
G,m = pg.populate_nodes(G)
G,m1=pg.populate_channels(G,m,645320)
G = pg.populate_policies(G,m1)

file1 = ["lnd.csv","lnd1.csv","lnd2.csv","lnd3.csv","lnd4.csv"]
file2 = ["c-lightning.csv","c-lightning1.csv","c-lightning2.csv","c-lightning3.csv","c-lightning4.csv"]
#file3 = ["eclair.csv","eclair1.csv","eclair2.csv","eclair3.csv","eclair4.csv"]
file4 = ["eclair10.csv","eclair11.csv","eclair12.csv","eclair13.csv","eclair14.csv"]
file5 = ["eclair20.csv","eclair21.csv","eclair22.csv","eclair23.csv","eclair24.csv"]
file6 = ["shortest.csv","shortest1.csv","shortest2.csv","shortest3.csv","shortest4.csv"]
file8 = ["cheapest.csv","cheapest1.csv","cheapest2.csv","cheapest3.csv","cheapest4.csv"]
file7 = ["least-delay.csv","least-delay1.csv","least-delay2.csv","least-delay3.csv","least-delay4.csv"]
#file9 = ["eclair_paths.csv","eclair_paths1.csv","eclair_paths2.csv","eclair_paths3.csv","eclair_paths4.csv"]
file10 = ["eclair_paths10.csv","eclair_paths11.csv","eclair_paths12.csv","eclair_paths13.csv","eclair_paths14.csv"]
file11 = ["eclair_paths20.csv","eclair_paths21.csv","eclair_paths22.csv","eclair_paths23.csv","eclair_paths24.csv"]


if __name__ == "__main__":
    a = int(sys.argv[1])
    G1 = nx.DiGraph()

    for [u,v] in G.edges():
        if(G.edges[u,v]["marked"]==1 and G.edges[v,u]["marked"]==1):
            if (u not in G1.nodes()):
                G1.add_node(u)
                G1.nodes[u]["name"] = G.nodes[u]["name"]
                G1.nodes[u]["pubadd"] = G.nodes[u]["pubadd"]
                G1.nodes[u]["Tech"] = G.nodes[u]["Tech"]
                #print(G1.nodes[u]["Tech"])
            if (v not in G1.nodes()):
                G1.add_node(v)
                G1.nodes[v]["name"] = G.nodes[v]["name"]
                G1.nodes[v]["pubadd"] = G.nodes[v]["pubadd"]
                G1.nodes[v]["Tech"] = G.nodes[v]["Tech"]
                #print(G1.nodes[v]["Tech"])
            G1.add_edge(u,v)
            G1.edges[u,v]["Balance"] = G.edges[u,v]["Balance"]
            G1.edges[u, v]["Age"] = G.edges[u, v]["Age"]
            G1.edges[u, v]["BaseFee"] = G.edges[u, v]["BaseFee"]
            G1.edges[u, v]["FeeRate"] = G.edges[u, v]["FeeRate"]
            G1.edges[u, v]["Delay"] = G.edges[u, v]["Delay"]
            G1.edges[u, v]["id"] = G.edges[u, v]["id"]
            G1.edges[u, v]["LastFailure"] = G.edges[u, v]["LastFailure"]

    def route(G,path,delay,amt):
        #print(path[0])
        G.edges[path[0],path[1]]["Balance"] -= amt
        G.edges[path[1],path[0]]["Locked"] = amt
        delay = delay - G.edges[path[0],path[1]]["Delay"]
        i = 1
        while(i < len(path)-1):
            #print(path[i])
            amt = (amt - G.edges[path[i], path[i+1]]["BaseFee"]) / (1 + G.edges[path[i], path[i+1]]["FeeRate"])
            # if path[i] in ads:
            #     delay1 = delay - G.edges[path[i],path[i+1]]["Delay"]
            #     print(delay1)
            #     B,flag = at.dest_reveal_new(G,path[i],delay1,amt,path[i-1],path[i+1])
            #     with open(file,'a') as csv_file:
            #         csvwriter = csv.writer(csv_file)
            #         for j in B:
            #             csvwriter.writerow([ind,path[i],j,B[j],flag])
            if(G.edges[path[i],path[i+1]]["Balance"] >= amt):
                G.edges[path[i], path[i+1]]["Balance"] -= amt
                G.edges[path[i+1], path[i]]["Locked"] = amt
                if i == len(path) - 2:
                    G.edges[path[i+1],path[i]]["Balance"] += G.edges[path[i+1], path[i]]["Locked"]
                    G.edges[path[i+1], path[i]]["Locked"] = 0
                    j = i - 1
                    while j >= 0:
                        G.edges[path[j + 1], path[j]]["Balance"] += G.edges[path[j + 1], path[j]]["Locked"]
                        G.edges[path[j + 1], path[j]]["Locked"] = 0
                        j = j-1
                    return True
                delay = delay - G.edges[path[i],path[i+1]]["Delay"]
                i += 1
            else:
                G.edges[path[i],path[i+1]]["LastFailure"] = 0
                j = i - 1
                while j >= 0:
                    G.edges[path[j],path[j+1]]["Balance"] += G.edges[path[j+1],path[j]]["Locked"]
                    G.edges[path[j + 1], path[j]]["Locked"] = 0
                    j = j-1
                return False

    def execute_lnd(G,source,destination,amt,i,file):
        path = []
        path,delay,amount,dist = pf.Dijkstra(G,source,destination,amt,pf.lnd_cost_fun)
        # with open(file, 'a') as csv_file:
        #     csvwriter = csv.writer(csv_file)
        #     csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount])
        if len(path)<2:
            T = False
        else:
            if(len(path)==2):
                G.edges[path[0], path[1]]["Balance"] -= amt
                G.edges[path[1], path[0]]["Balance"] += amt
                with open(file, 'a') as csv_file:
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, True])
                return True
            else:
                T = route(G,path,delay,amount)
        if(T == True):
            with open(file,'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i,source,destination,amt,path,len(path),delay,amount,T])
            return True
        else:
            c = 0
            while T == False and c<=10:
                path = []
                path, delay, amount,dist = pf.Dijkstra(G, source, destination, amt,pf.lnd_cost_fun)
                if len(path)<2:
                    with open(file, 'a') as csv_file:
                        csvwriter = csv.writer(csv_file)
                        csvwriter.writerow([i, source, destination, amt, [], 0, 0, 0, T])
                    return False
                else:
                    T = route(G, path, delay,amount)
                    if T == True or c == 10:
                        with open(file, 'a') as csv_file:
                            csvwriter = csv.writer(csv_file)
                            csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, T])
                        return True
                    else:
                        c+=1
    def execute_c_lightning(G,source,destination,amt,i,file):
        fuzz = rn.uniform(-1,1)
        path = []
        path,delay,amount,dist = pf.Dijkstra(G,source,destination,amt,pf.c_cost_fun(fuzz))
        if len(path)<2 or len(path) >= 20:
            with open(file,'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i,source,destination,amt,[],0,0,0,False])
            return False
        if (len(path) == 2):
            G.edges[path[0], path[1]]["Balance"] -= amt
            G.edges[path[1], path[0]]["Balance"] += amt
            with open(file, 'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, True])
            return True
        T = route(G,path,delay,amount)
        with open(file, 'a') as csv_file:
            csvwriter = csv.writer(csv_file)
            csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, T])
        return T

    # def execute_eclair(G,source,destination,amt,i,file):
    #     path = []
    #     B = pf.Eclair(G,source,destination,amt)
    #     with open(file9[a], 'a') as csv_file:
    #         csvwriter = csv.writer(csv_file)
    #         csvwriter.writerow([i, source, destination, amt, B[0],B[1],B[2]])
    #     if len(B[0])==2 or len(B[0])==0:
    #         r = 0
    #         path = B[r]
    #     else:
    #         while path == {} or path == []:
    #             r = rn.randint(0, 2)
    #             r = min(len(B)-1,r)
    #             path = B[r]
    #     delay = 0
    #     amount = amt
    #     #print(path, r)
    #     if (len(path) > 2):
    #         for m in range(len(path) - 2, 0, -1):
    #             delay += G1.edges[path[m], path[m + 1]]["Delay"]
    #             amount += G1.edges[path[m], path[m + 1]]["BaseFee"] + amount * G1.edges[path[m], path[m + 1]]["FeeRate"]
    #         delay += G1.edges[path[0], path[1]]["Delay"]
    #     if len(path)<2:
    #         with open(file, 'a') as csv_file:
    #             csvwriter = csv.writer(csv_file)
    #             csvwriter.writerow([i, source, destination, amt, [], 0, 0, 0, False])
    #         return False
    #     if (len(path) == 2):
    #         G.edges[path[0], path[1]]["Balance"] -= amt
    #         G.edges[path[1], path[0]]["Balance"] += amt
    #         with open(file, 'a') as csv_file:
    #             csvwriter = csv.writer(csv_file)
    #             csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, True])
    #         return True
    #     T = route(G,path,delay,amount)
    #     with open(file, 'a') as csv_file:
    #         csvwriter = csv.writer(csv_file)
    #         csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, T])
    #     return T

    def execute_eclair_modified(G,source,destination,amt,i,file):
        path = []
        B = pf.modifiedEclair(G,source,destination,amt)
        with open(file10[a], 'a') as csv_file:
            csvwriter = csv.writer(csv_file)
            csvwriter.writerow([i, source, destination, amt, B[0],B[1],B[2]])
        if len(B[0])==2 or len(B[0]) == 0:
            r = 0
            path = B[r]
        else:
            while path == {} or path == []:
                r = rn.randint(0, 2)
                r = min(len(B) - 1, r)
                path = B[r]
        delay = 0
        amount = amt
        #print(path, r)
        if (len(path) > 2):
            for m in range(len(path) - 2, 0, -1):
                delay += G1.edges[path[m], path[m + 1]]["Delay"]
                amount += G1.edges[path[m], path[m + 1]]["BaseFee"] + amount * G1.edges[path[m], path[m + 1]]["FeeRate"]
            delay += G1.edges[path[0], path[1]]["Delay"]
        if len(path)<2:
            with open(file, 'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i, source, destination, amt, [], 0, 0, 0, False])
            return False
        if (len(path) == 2):
            G.edges[path[0], path[1]]["Balance"] -= amt
            G.edges[path[1], path[0]]["Balance"] += amt
            with open(file, 'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, True])
            return True
        T = route(G,path,delay,amount)
        with open(file, 'a') as csv_file:
            csvwriter = csv.writer(csv_file)
            csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, T])
        return T

    def execute_eclair_noyen(G,source,destination,amt,i,file):
        path = []
        B = pf.Dijkstra_general(G,source,destination,amt,pf.eclair_cost_fun)
        with open(file11[a], 'a') as csv_file:
            csvwriter = csv.writer(csv_file)
            csvwriter.writerow([i, source, destination, amt, B[0],B[1],B[2]])
        if len(B[0])==2:
            r = 0
        else:
            r = rn.randint(0, 2)
            r = min(len(B)-1,r)
        path = B[r]
        delay = 0
        amount = amt
        #print(path, r)
        if (len(path) > 2):
            for m in range(len(path) - 2, 0, -1):
                delay += G1.edges[path[m], path[m + 1]]["Delay"]
                amount += G1.edges[path[m], path[m + 1]]["BaseFee"] + amount * G1.edges[path[m], path[m + 1]]["FeeRate"]
            delay += G1.edges[path[0], path[1]]["Delay"]
        if len(path)<2:
            with open(file, 'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i, source, destination, amt, [], 0, 0, 0, False])
            return False
        if (len(path) == 2):
            G.edges[path[0], path[1]]["Balance"] -= amt
            G.edges[path[1], path[0]]["Balance"] += amt
            with open(file, 'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, True])
            return True
        T = route(G,path,delay,amount)
        with open(file, 'a') as csv_file:
            csvwriter = csv.writer(csv_file)
            csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, T])
        return T

    def execute_shortest(G,source,destination,amt,i,file):
        path = []
        path, delay, amount,dist = pf.Dijkstra(G, source, destination, amt,pf.shortest_cost_fun)
        if len(path) < 2:
            with open(file, 'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i, source, destination, amt, [], 0, 0, 0, False])
            return False
        if (len(path) == 2):
            G.edges[path[0], path[1]]["Balance"] -= amt
            G.edges[path[1], path[0]]["Balance"] += amt
            with open(file, 'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, True])
            return True
        T = route(G, path,delay, amount)
        with open(file, 'a') as csv_file:
            csvwriter = csv.writer(csv_file)
            csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, T])
        return T

    def execute_least_delay(G,source,destination,amt,i,file):
        path = []
        path, delay, amount, dist = pf.Dijkstra(G, source, destination, amt, pf.least_delay_cost_fun)
        if len(path) < 2:
            with open(file, 'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i, source, destination, amt, [], 0, 0, 0, False])
            return False
        if (len(path) == 2):
            G.edges[path[0], path[1]]["Balance"] -= amt
            G.edges[path[1], path[0]]["Balance"] += amt
            with open(file, 'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, True])
            return True
        T = route(G, path, delay, amount)
        with open(file, 'a') as csv_file:
            csvwriter = csv.writer(csv_file)
            csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, T])
        return T

    def execute_cheapest(G,source,destination,amt,i,file):
        path = []
        path, delay, amount, dist = pf.Dijkstra(G, source, destination, amt, pf.cheapest_cost_fun)
        if len(path) < 2:
            with open(file, 'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i, source, destination, amt, [], 0, 0, 0, False])
            return False
        if (len(path) == 2):
            G.edges[path[0], path[1]]["Balance"] -= amt
            G.edges[path[1], path[0]]["Balance"] += amt
            with open(file, 'a') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, True])
            return True
        T = route(G, path, delay, amount)
        with open(file, 'a') as csv_file:
            csvwriter = csv.writer(csv_file)
            csvwriter.writerow([i, source, destination, amt, path, len(path), delay, amount, T])
        return T

    with open(file1[a],'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow("i,s,d,amt,path,len,amt1,del,suc")
    with open(file2[a],'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow("i,s,d,amt,path,len,amt1,del,suc")
    # with open(file3[a],'w') as csv_file:
    #     csvwriter = csv.writer(csv_file)
    #     csvwriter.writerow("i,s,d,amt,path,len,amt1,del,suc")
    with open(file4[a],'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow("i,s,d,amt,path,len,amt1,del,suc")
    with open(file5[a],'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow("i,s,d,amt,path,len,amt1,del,suc")
    with open(file6[a],'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow("i,s,d,amt,path,len,amt1,del,suc")
    with open(file7[a],'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow("i,s,d,amt,path,len,amt1,del,suc")
    with open(file8[a],'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow("i,s,d,amt,path,len,amt1,del,suc")
    # with open(file9[a],'w') as csv_file:
    #     csvwriter = csv.writer(csv_file)
    #     csvwriter.writerow("i,s,d,amt,path,len,amt1,del,suc")
    with open(file10[a],'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow("i,s,d,amt,path,len,amt1,del,suc")
    with open(file11[a],'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow("i,s,d,amt,path,len,amt1,del,suc")
    i = 0
    G2 = G1.copy()
    #G3 = G1.copy()
    G4 = G1.copy()
    G5 = G1.copy()
    G6 = G1.copy()
    G7 = G1.copy()
    G8 = G1.copy()
    while(i<=10000):
        u = -1
        v = -1
        while (u == v or (u not in G1.nodes()) or (v not in G1.nodes())):
            u = rn.randint(0, 11197)
            v = rn.randint(0, 11197)
        if (i % 5 == 1):
            amt = rn.randint(1, 10)
        elif (i % 5 == 2):
            amt = rn.randint(10, 100)
        elif (i % 5 == 3):
            amt = rn.randint(100, 1000)
        elif (i % 5 == 4):
            amt = rn.randint(1000, 10000)
        else:
            amt = rn.randint(10000, 100000)
        T1 = execute_lnd(G1,u,v,amt,i,file1[a])
        T2 = execute_c_lightning(G2,u,v,amt,i,file2[a])
        #T3 = execute_eclair(G3,u,v,amt,i,file3[a])
        T4 = execute_eclair_modified(G4,u,v,amt,i,file4[a])
        T5 = execute_eclair_noyen(G5,u,v,amt,i,file5[a])
        T6 = execute_shortest(G6,u,v,amt,i,file6[a])
        T7 = execute_least_delay(G7,u,v,amt,i,file7[a])
        T8 = execute_cheapest(G8,u,v,amt,i,file8[a])
        for [u,v] in G1.edges():
            G1.edges[u,v]["LastFailure"] += 0.25
            G2.edges[u, v]["LastFailure"] += 0.25
            #G3.edges[u, v]["LastFailure"] += 0.25
            G4.edges[u, v]["LastFailure"] += 0.25
            G5.edges[u, v]["LastFailure"] += 0.25
            G6.edges[u, v]["LastFailure"] += 0.25
            G7.edges[u, v]["LastFailure"] += 0.25
            G8.edges[u, v]["LastFailure"] += 0.25
        i+=1