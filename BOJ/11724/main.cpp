#include <bits/stdc++.h>
using namespace std;

int graph[10001][10001];
set<int> vertex;

void BFS(pair<int, int> inputpos, pair<int, int> range) {
    pair<int, int> pos;
    queue<pair<int, int>> queue;
    queue.push(inputpos);
    graph[inputpos.first][inputpos.second] = -1;
    while (!queue.empty()) {
        // preemptive check
        pos = queue.front();
        queue.pop();
        // u
        for (int u = range.first; u <= pos.first; u++) {
            if (graph[u][pos.first] == 1) {
                graph[u][pos.first] = -1;
                queue.push(pair(u, pos.first));
            }
        }
        for (int u = pos.first; u <= range.second; u++) {
            if (graph[pos.first][u] == 1) {
                graph[pos.first][u] = -1;
                queue.push(pair(pos.first, u));
            }
        }
        // v
        for (int v = range.first; v <= pos.second; v++) {
            if (graph[v][pos.second] == 1) {
                graph[v][pos.second] = -1;
                queue.push(pair(v, pos.second));
            }
        }
        for (int v = pos.second; v <= range.second; v++) {
            if (graph[pos.second][v] == 1) {
                graph[pos.second][v] = -1;
                queue.push(pair(pos.second, v));
            }
        }
    }
}

void solve() {
    vertex.clear();
    int N, M;
    cin >> N >> M;
    for (int m = 0; m < M; m++) {
        int u, v;
        cin >> u >> v;
        if (u <= v) {
            graph[u][v] = 1;
        } else {
            graph[v][u] = 1;
        }
        vertex.insert(u);
        vertex.insert(v);
    }
    if (vertex.empty()) {
        cout << N;
        return;
    }

    int min = *vertex.begin();
    int max = *vertex.rbegin();
    int count = N - vertex.size();
    for (int idx_x = min; idx_x <= max; idx_x++) {
        for (int idx_y = idx_x; idx_y <= max; idx_y++) {
            if (graph[idx_x][idx_y] == 1) {
                BFS(pair(idx_x, idx_y), pair(min, max));
                count++;
            }
        }
    }
    cout << count << "\n";
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
