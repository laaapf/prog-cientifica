using JSON

function readJSON(filename)
  open(filename, "r") do fid
    data = JSON.parse(fid)
    if haskey(data, "coordinates")
      nE = size(data["coordinates"])[1]
      x0 = Array{Float64}(undef, nE, 1)
      y0 = Array{Float64}(undef, nE, 1)
      for i = 1:nE
        x0[i] = convert(Float64, data["coordinates"][i][1])
        y0[i] = convert(Float64, data["coordinates"][i][2])
      end
    else
      println("ERRO: Não é possível ler 'coordinates' do JSON.")
      exit()
    end
    if haskey(data, "connect")
      connect = convert(Array{Int64}, data["connect"])
    else
      println("ERRO: Não é possível ler 'connect' do JSON.")
      exit()
    end
    if haskey(data, "raio")
      raio = convert(Float64, data["raio"])
    else
      println("ERRO: Não é possível ler 'raio' do JSON.")
      exit()
    end
    if haskey(data, "f")
      f = convert(Array{Float64}, data["f"])
    else
      println("ERRO: Não é possível ler 'f' do JSON.")
      exit()
    end
    if haskey(data, "restricoes")
      restricoes = convert(Array{Float64}, data["restricoes"])
    else
      println("ERRO: Não é possível ler 'restricoes' do JSON.")
      exit()
    end
    return nE, x0, y0, raio, f, restricoes, connect
  end
end

function outputRes(_res)
  dict = Dict()
  push!(dict,"resultado"=>_res)
  open("output.json","w") do f
      JSON.print(f,dict)
  end
end

function main(filename)
  nE, x0, y0, raio, f, restricoes, connect = readJSON(filename)
  println(nE)
  @show raio
  @show f
  @show restricoes
  @show connect

  # tamanho de passo
  h = 0.00002
  # h = 0.00004
  # h = 0.00008
  # h = 0.00016
  # h = 0.00032

  # numero de passos
  N = 2000
  # N = 1000
  # N = 500
  # N = 250
  # N = 125


  m = 7850.0 #massa
  k = 210000000000.0  # 210 * 10^9 de rigidez entre duas particulas

  # número de equações(2 DOFs por particulas)
  nDOFs = nE * 2

  a = zeros(Float64, nDOFs, 1)# aceleracao
  v = zeros(Float64, nDOFs, 1) # velocidade
  u = zeros(Float64, nDOFs, 1) # vetores deslocamento
  fi = zeros(Float64, nDOFs, 1) # forças internas
  ux_hist = zeros(Float64, N, 1)
  result_index = 4*2 - 1 # deslocamento da particula

  # Equação: F_ext - ku = mü
  # ü = (f - f_i) / m
  a .= (f .- fi)./ m 
  # Leapfrog
  for ii = 1:N
    v .+= a.*(0.5*h)
    u .+= v.*h

    # Algoritmo de contato (calculando forças internas)
    fi .= 0.0
    for jj = 1:nE
      
      u[jj*2-1] *= 1 - restricoes[jj*2-1]
      x_j = x0[jj] + u[jj*2-1]
      u[jj*2]   *= 1 - restricoes[jj*2]
      y_j = y0[jj] + u[jj*2]

      for ww = 1:connect[(jj-1)*5+1]
        neighbor = connect[(jj-1)*5 + ww+1]
        x_w = x0[neighbor] + u[neighbor*2-1] #alterar aqui para usar vetor
        y_w = y0[neighbor] + u[neighbor*2]
        dx = x_j - x_w
        dy = y_j - y_w
        d = sqrt(dx*dx + dy*dy)
        spring_deform = d - 2*raio
        dx = spring_deform * dx / d
        dy = spring_deform * dy / d
        fi[jj*2-1] += k*dx
        fi[jj*2]   += k*dy
      end
    end

    ux_hist[ii] = u[result_index]

    a .= (f .- fi)./ m
    v .+= a.*(0.5*h)
  end

  outputRes(ux_hist)
end

if (length(ARGS)==1)
  main(ARGS[1])
end