
using JSON

function main()
    print("Digite Ta:")
    s = readline()
    Ta = parse(Float64, s)
    print("Digite Tb:")
    s = readline()
    Tb = parse(Float64, s)
    print("Digite Tinf:")
    s = readline()
    Tinf = parse(Float64, s)
    print("Digite delta_x:")
    s = readline()
    delta_x = parse(Float64, s)
    print("Digite hlinha:")
    s = readline()
    hlinha = parse(Float64, s)
    print("Digite h:")
    s = readline()
    h = parse(Float64, s)
    print("Digite L:")
    s = readline()
    L = parse(Float64, s)
    print("Digite k:")
    s = readline()
    k = parse(Float64, s)
    print("Digite r:")
    s = readline()
    r = parse(Float64, s)

    outputRes(Ta,Tb,Tinf,L,k,r,h,hlinha,delta_x)
end

function outputRes(_Ta, _Tb, _Tinf, _L, _k, _r,_h,_hlinha,_delta_x)
    dict = Dict()
    push!(dict,"Ta"=>_Ta)
    push!(dict,"Tb"=>_Tb)
    push!(dict,"Tinf"=>_Tinf)
    push!(dict,"L"=>_L)
    push!(dict,"k"=>_k)
    push!(dict,"r"=>_r)
    push!(dict,"h"=>_h)
    push!(dict,"hlinha"=>_hlinha)
    push!(dict,"delta_x"=>_delta_x)
    open("input.json","w") do f
        JSON.print(f,dict)
    end
end

if (length(ARGS)==0)
    main()
end