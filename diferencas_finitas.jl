using Plots
using JSON


function var_A(_Ta,_Tb,_Tinf,_Lamb,_L)
    A = (((_Ta-_Tinf)*(ℯ^(-_Lamb*_L)))-(_Tb-_Tinf))/(ℯ^(-_Lamb*_L)-ℯ^(_Lamb*_L))
    return A
end

function var_B(_Ta,_Tb,_Tinf,_Lamb,_L)
    B = ((_Tb-_Tinf)-((_Ta-_Tinf)*ℯ^(_Lamb*_L)))/(ℯ^(-_Lamb*_L)-ℯ^(_Lamb*_L))
    return B
end

function analitica(_Ta,_Tb,_Tinf,hlinha,_L,_x)
    elements::UInt16 = _L/_x
    f = zeros(Float64, elements + 1)
    t = zeros(Float64, elements + 1)
    ti = 0
    lamb = sqrt(hlinha)
    A = var_A(_Ta,_Tb,_Tinf,lamb,_L)
    B = var_B(_Ta,_Tb,_Tinf,lamb,_L)
    Tx = _Tinf + A*ℯ^(lamb*ti) + B*ℯ^(-lamb*ti)
    f[1] = Tx
    t[1] = ti


    for i=1:elements
        ti = ti + _x
        Tx = _Tinf + A*ℯ^(lamb*ti) + B*ℯ^(-lamb*ti)
        
        t[i+1] = ti
        f[i+1] = Tx
    end

    return f, t 
end

function dif_finitas(_Ta,_Tb,_Tinf,_hlinha,_L,_x)
    elements::UInt16 = _L/_x

    A = zeros(Float64, (elements-1,elements-1))
    b = zeros(Float64, elements-1)
    f = zeros(Float64, elements+1)

    f[1] = _Ta
    f[elements+1] = _Tb

    r_side_equation = _x^2*_hlinha*_Tinf
    Ti = 2+(_x^2)*_hlinha

    for i=1:elements-1
        if i == 1 || i == elements - 1
            b[i] = r_side_equation
            if i == 1
                A[1,1] = Ti
                b[i] += _Ta
                if elements - 1 > 1
                    A[1,2] = -1
                end
            end
            if i == elements-1
                A[i,i] = Ti
                b[i] += _Tb
                if elements - 1 > 1
                    A[i,i-1] = -1
                end
            end
        else
            b[i] = r_side_equation
            A[i,i] = Ti
            A[i,i+1] = -1
            A[i,i-1] = -1
        end
    end
    result = A\b
    for i=1:elements-1
        f[i+1] = result[i]
    end
    @show f
    return f
end



function main(filename)
    Ta, Tb, Tinf, L, k, r,h,hlinha,delta_x = readJSON(filename)
    @show Ta
    @show Tb
    @show Tinf
    @show L
    @show k
    @show r
    @show h
    @show hlinha
    @show delta_x

    w1,t1 = analitica(Ta,Tb,Tinf,hlinha,L,delta_x)
    w2 = dif_finitas(Ta,Tb,Tinf,hlinha,L,delta_x)

    print("\n")
    print(w1)
    print("\n")
    print(t1)


    ylabel!("T em Kelvin")
    xlabel!("x")
    # plot!(t1, w1,label = "Analitica")
    # plot!(t1, w2,label = "Diferencas Finitas")
    plot!(t1,w2-w1,label = "Erro")

    png("plot")
    outputRes(w1,t1,w2)
end

function readJSON(filename)
    open(filename, "r") do fid
      data = JSON.parse(fid)
      if haskey(data, "Ta")
        Ta = convert(Float64, data["Ta"])
      else
        println("ERRO: Não é possível ler 'Ta' do JSON.")
        exit()
      end
      if haskey(data, "Tb")
        Tb = convert(Float64, data["Tb"])
      else
        println("ERRO: Não é possível ler 'Tb' do JSON.")
        exit()
      end
      if haskey(data, "Tinf")
        Tinf = convert(Float64, data["Tinf"])
      else
        println("ERRO: Não é possível ler 'Tinf' do JSON.")
        exit()
      end
      if haskey(data, "L")
        L = convert(Float64, data["L"])
      else
        println("ERRO: Não é possível ler 'L' do JSON.")
        exit()
      end
      if haskey(data, "k")
        k = convert(Float64, data["k"])
      else
        println("ERRO: Não é possível ler 'raio' do JSON.")
        exit()
      end
      if haskey(data, "r")
        r = convert(Float64, data["r"])
      else
        println("ERRO: Não é possível ler 'r' do JSON.")
        exit()
      end
      if haskey(data, "h")
        h = convert(Float64, data["h"])
      else
        println("ERRO: Não é possível ler 'h' do JSON.")
        exit()
      end
      if haskey(data, "hlinha")
        hlinha = convert(Float64, data["hlinha"])
      else
        println("ERRO: Não é possível ler 'hlinha' do JSON.")
        exit()
      end
      if haskey(data, "delta_x")
        delta_x = convert(Float64, data["delta_x"])
      else
        println("ERRO: Não é possível ler 'delta_x' do JSON.")
        exit()
      end
      return Ta, Tb, Tinf, L, k, r,h,hlinha,delta_x
    end
end

function outputRes(_resultAnalitico,_x,_resultDiv)
    dict = Dict()
    push!(dict,"x"=>_x)
    push!(dict,"resultado_analitico"=>_resultAnalitico)
    push!(dict,"resultado_diferencas_finitas"=>_resultDiv)
    open("output.json","w") do f
        JSON.print(f,dict)
    end
end

if (length(ARGS)==1)
    main(ARGS[1])
end