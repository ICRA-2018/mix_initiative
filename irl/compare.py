import networkx as nx
import random
import sys
import time


def create_graph(N=1000, d=10): 
    #G = nx.random_regular_graph(d,N)
    D = nx.gn_graph(N,kernel=lambda x:x**(-40))
    G = D.to_undirected()
    for e in G.edges():
        G.edge[e[0]][e[1]]['cost'] = random.random()*30
        G.edge[e[0]][e[1]]['distance'] = random.randint(0,10)
    G.graph['start'] = 0
    G.graph['goal'] = N-1
    return G

def param_dijkstra(G, beta):
    start = G.graph['start']
    goal = G.graph['goal']
    G_beta = nx.DiGraph()
    for e in G.edges():
        G_beta.add_edge(e[0],e[1],
                        weight=evaluate_edge_cost(G,e,beta))
    path = nx.shortest_path(G_beta, start, goal)
    return path

def margin_opt_path(G, opt_path, beta):
    start = G.graph['start']
    goal = G.graph['goal']
    path_edges = zip(opt_path[0::2], opt_path[1::2])
    G_beta = nx.DiGraph()
    for e in G.edges():
        if e in path_edges:
            k = 1
        else:
            k = 0
        w = evaluate_edge_cost(G,e,beta)-k
        G_beta.add_edge(e[0], e[1], weight=w)
    path = nx.shortest_path(G_beta, start, goal)
    return path    

def evaluate_edge_cost(G, e, beta):
    c = G.edge[e[0]][e[1]]['cost']
    d = G.edge[e[0]][e[1]]['distance']
    return c+beta*d
    
def compute_path_cost(G, path, beta):
    cost = 0
    for i in range(len(path)-1):
        e = (path[i], path[i+1])
        cost += evaluate_edge_cost(G, e, beta)
    return cost

def compute_path_d(G, path):
    ac_d = 0
    for i in range(len(path)-1):
        e = (path[i], path[i+1])
        ac_d += G.edge[e[0]][e[1]]['distance']
    return ac_d
        
def opt_path_match(path1, path2):
    score = 0
    for i,s in enumerate(path1):
        if path2[i] == s:
            score += 1
    return score

def find_beta_via_enumeration(G, opt_path, opt_beta):
    print '------------------------------'
    print 'Find beta via enumeration starts'
    t0 = time.time()
    opt_cost = compute_path_cost(G, opt_path, opt_beta)
    beta_list = range(1,50)
    match_score = []
    cost_list = []
    for beta in beta_list:
        beta_best_path = param_dijkstra(G, beta)
        score = opt_path_match(opt_path, beta_best_path)
        cost = compute_path_cost(G, beta_best_path, beta)
        match_score.append(score)
        cost_list.append(cost)
    index_min = min(range(len(match_score)), key= lambda j: match_score[j])
    best_beta = beta_list[index_min]
    print 'In total %d para_dijkstra run.' %len(beta_list)
    print 'Best_beta found: %.2f ||| Given opt_beta: %.2f' %(best_beta, opt_beta)
    print 'Given optimal path cost: %.2f ||| Beta optimal path cost: %.2f ||| match score: %d ' %(opt_cost, cost_list[index_min], match_score[index_min])
    print 'Find beta via enumeration done, time %.2f' %(time.time()-t0)
    return best_beta, beta_list, cost_list, match_score

def irl(G, opt_path, opt_beta):
    print '------------------------------'
    print 'Find beta via IRL starts'
    t0 = time.time()
    opt_cost = compute_path_cost(G, opt_path, opt_beta)
    beta = 100
    beta_p = 10
    count = 0
    lam = 1
    alpha = 1
    while (abs(beta_p-beta)>0.3):
        print 'Iteration --%d--'%count
        beta = beta_p
        opt_ac_d = compute_path_d(G, opt_path)
        marg_path = margin_opt_path(G, opt_path, beta)
        marg_ac_d = compute_path_d(G, marg_path)
        gradient = beta + lam*(opt_ac_d-marg_ac_d)
        beta_p = beta - (alpha/(count+1))*gradient
        count += 1
    print 'old beta: %.2f ||| new beta: %.2f' %(beta, beta_p)
    print 'In total %d para_dijkstra run.' %len(count)
    print 'Best_beta found: %.2f ||| Given opt_beta: %.2f' %(beta_p, opt_beta)
    print 'Find beta via IRL done, time %.2f' %(time.time()-t0)
    return beta_p


G = create_graph()
opt_beta = 30
opt_path = param_dijkstra(G, opt_beta)
print 'Given optimal path length: %d ||| Given beta: %.2f' %(len(opt_path), opt_beta)
best_beta, beta_list, cost_list, match_score = find_beta_via_enumeration(G, opt_path, opt_beta)
    

        
    


