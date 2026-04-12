#include <bits/stdc++.h>
using namespace std;

void solve() {
    int a, b, c, d, e, f;
    cin >> a >> b >> c >> d >> e >> f;
    // ax + by = c
    // dx + ey = f
    // adx + bdy = cd
    // adx + aey = af
    // y = (cd-af)/(bd-ae)
    // aex + bey = ce
    // bdx + bey = bf
    // x = (ce-bf)/(ae-bd)
    cout << ((c * e - b * f) / (a * e - b * d)) << " " << ((c * d - a * f) / (b * d - a * e));
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
