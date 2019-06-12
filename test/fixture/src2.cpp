#include <fstream>
#include <iostream>
#include <vector>
#include <iterator>
#include <algorithm>
using namespace std;

double signed_area(int x1,int y1,int x2, int y2, int x3, int y3)
{
    double result;
    result = (x1*y2) + (x2*y3) + (x3*y1) - (y1*x2) - (y2*x3) - (y3*x1);
    if(result >0)
        result = 1;
    if(result <0)
        result = -1;
    if(result == 0)
        result = 0;
    return result;
}

int main()
{
    ifstream infile("polygon.inp");
    ofstream outfile("polygon.out");
    double N,i,prior_k,k,concave_k=0,t=0,h=0,l,k_,k2,k3,m=1;
    infile >> N;
    l = N+1;
    vector<vector<int>> poly(N, vector<int>(2) );
    for(i=0 ; i<N ; i++){
        infile >> poly[i][0] >> poly[i][1];
        //cout << poly[i][0] << " " << poly[i][1] << endl;
    }
    for(i=0 ; i<N ; i++){
        if ( i == l+2 && h==1){
            h = 0;
        }
        if( i<N-3 ){
            k = signed_area(poly[i][0],poly[i][1], poly[i+1][0], poly[i+1][1], poly[i+2][0], poly[i+2][1]);
            k_ = signed_area(poly[i][0],poly[i][1], poly[i+1][0], poly[i+1][1], poly[i+3][0], poly[i+3][1]);
            k3 = signed_area(poly[i+2][0],poly[i+2][1], poly[i+3][0], poly[i+3][1], poly[i+1][0], poly[i+1][1]);
            k2 = signed_area(poly[i+2][0],poly[i+2][1], poly[i+3][0], poly[i+3][1], poly[i][0], poly[i][1]);
        }
        if( i == N-3){
            k = signed_area(poly[i][0],poly[i][1], poly[i+1][0], poly[i+1][1], poly[i+2][0], poly[i+2][1]);
            k_ = signed_area(poly[i][0],poly[i][1], poly[i+1][0], poly[i+1][1], poly[0][0], poly[0][1]);
            k3 = signed_area(poly[i+2][0],poly[i+2][1], poly[0][0], poly[0][1], poly[i+1][0], poly[i+1][1]);
            k2 = signed_area(poly[i+2][0],poly[i+2][1], poly[0][0], poly[0][1], poly[i][0], poly[i][1]);
        }
        if( i==N-2 ){
            k = signed_area(poly[i][0],poly[i][1], poly[i+1][0], poly[i+1][1], poly[0][0], poly[0][1]);
            k_ = signed_area(poly[i][0],poly[i][1], poly[i+1][0], poly[i+1][1], poly[1][0], poly[1][1]);
            k3 = signed_area(poly[0][0],poly[0][1], poly[1][0], poly[1][1], poly[i+1][0], poly[i+1][1]);
            k2 = signed_area(poly[0][0],poly[0][1], poly[1][0], poly[1][1], poly[i][0], poly[i][1]);
        }
        if( i==N-1 ){
            k = signed_area(poly[i][0],poly[i][1], poly[0][0], poly[0][1], poly[1][0], poly[1][1]);
            k_ = signed_area(poly[i][0],poly[i][1], poly[0][0], poly[0][1], poly[2][0], poly[2][1]);
            k3 = signed_area(poly[1][0],poly[1][1], poly[2][0], poly[2][1], poly[i][0], poly[i][1]);
            k2 = signed_area(poly[1][0],poly[1][1], poly[2][0], poly[2][1], poly[0][0], poly[0][1]);
        }
        if(i != 0 && i != N-1){
            m = signed_area(poly[0][0],poly[0][1], poly[i][0], poly[i][1], poly[N-1][0], poly[N-1][1]);
            if(m == 0){
                    //outfile << "None";
                    t=1;
                    break;
            }
        }
        if(i==0 ){
            if(  (k_ * k < 0 && k2 *k3 <0) || k == 0  ){
                //cout << "None" << endl;
                //outfile << "None";
                t=1;
                break;
            }
        }
        if(i>0 ){
            if(k != 0 && k_ ==0){
                if(k2 * k3 <0){
                    //outfile << "None";
                    t=1;
                    break;
                }
            }
            if(k_ != 0 && k ==0){
                if(k2 * k3 <0){
                    //outfile << "None";
                    t=1;
                    break;
                }
            }
            if(k2 != 0 && k3 ==0){
                if(k * k_ <0){
                    //outfile << "None";
                    t=1;
                    break;
                }
            }
            if(k3 != 0 && k2 ==0){
                if(k * k_ <0){
                    //outfile << "None";
                    t=1;
                    break;
                }
            }
            if(  k_ * k < 0 && k2 *k3 <0  ){
                //cout << "None" << endl;
                //outfile << "None";
                t=1;
                break;
            }
            if(prior_k < 0 ){
                if(k>0){
                    if(h == 0){
                        concave_k ++;
                        h = 1;
                        l = i;
                    }
                    else if(h == 1)
                        h = 0;

                }
            }
            else if(prior_k > 0 ){
                if(k<0){
                    if(h == 0){
                        concave_k ++;
                        h = 1;
                        l = i;
                    }
                    else if(h == 1)
                        h = 0;
                }
            }
        }
        prior_k = k;

    }
    if(t==1){
        outfile << "None";
    }
    if(concave_k>0 && t == 0){
        //cout << "Concave" << concave_k << endl;
        outfile << "Concave " << concave_k;
    }
    else if ( concave_k ==0 && t == 0){
        //cout << "Convex" << endl;
        outfile << "Convex";
    }

    infile.close();
    outfile.close();
}
