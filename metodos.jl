using Plots

function func(_t, _u) #temos u' = p0*sin(t) sendo p0 = 1
    y = sin(_t)
    return y
end

function euler(_a, _b, _y0, _N)
    h = (_b -_a)/_N
    print(h)
    u = zeros(Float64, _N+1)
    t = zeros(Float64, _N+1)
    ui = _y0
    ti = _a
    u[1] = ui
    t[1] = ti

    for i = 1:_N
        ti = _a + i * h
        ui = ui + func(ti, ui)*h
        u[i+1] = ui
        t[i+1] = ti
    end
    
    return t, u
end

function rungeKutta(_a, _b, _y0, _N)
    h = (_b -_a)/_N
    u = zeros(Float64, _N+1)
    t = zeros(Float64, _N+1)
    ui = _y0
    ti = _a

    for i = 1:_N
        u[i] = ui
        t[i] = ti
        
        k1 = func(ti, ui)
        k2 = func(ti + h/2, ui+ k1*(h/2))
        k3 = func(ti + h/2, ui+ k2*(h/2))
        k4 = func(ti + h, ui+ k3*h)
        ui = ui + (((k1+ (k2*2)+ (k3*2)+ k4))*h/6)
        ti = _a + i * h
    end
    u[_N+1] = ui
    t[_N+1] = ti
    return t, u
end

function adamsBashforth(_a,_b,_y0,_N)
    h = (_b -_a)/_N
    u = zeros(Float64, _N+1)
    t = zeros(Float64, _N+1)
    ui = _y0
    ti = _a

    for i=1:4
        u[i]= ui
        t[i] = ti
        if i != 4
            k1 = func(ti, ui)
            k2 = func(ti + h/2, ui+ k1*(h/2))
            k3 = func(ti + h/2, ui+ k2*(h/2))
            k4 = func(ti + h, ui+ k3*h)
            ui = ui + (((k1+ (k2*2)+ (k3*2)+ k4))*h/6)
            ti = _a + i * h
        end
    end

    for i=4:_N
        ui = ui + (((func(t[i],u[i])*55)+(func(t[i-1],u[i-1])*-59)+(func(t[i-2],u[i-2])*37)+(func(t[i-3],u[i-3])*-9))*h/24)
        ti = _a + i * h 
        u[i+1] = ui
        t[i+1] = ti
    end 
    return t,u
end

function adamsMoulton(_a,_b,_y0,_N)
    h = (_b -_a)/_N
    u = zeros(Float64, _N+1)
    t = zeros(Float64, _N+1)
    ui = _y0
    ti = _a

    for i=1:4
        u[i] = ui
        t[i] = ti
        if i != 4
            k1 = func(ti, ui)
            k2 = func(ti + h/2, ui+ k1*(h/2))
            k3 = func(ti + h/2, ui+ k2*(h/2))
            k4 = func(ti + h, ui+ k3*h)
            ui = ui + (((k1+ (k2*2)+ (k3*2)+ k4))*h/6)
            ti = _a + i * h
        end
    end

    for i=4:_N
        ti = _a + i * h 
        up = ui + (((func(t[i],u[i])*55)+(func(t[i-1],u[i-1])*-59)+(func(t[i-2],u[i-2])*37)+(func(t[i-3],u[i-3])*-9))*h/24)
        ui = ui + (((func(ti,up)*9)+(func(t[i],u[i])*19)+(func(t[i-1],u[i-1])*-5)+(func(t[i-2],u[i-2])))*h/24)
        u[i+1] = ui
        t[i+1] = ti
    end

    return t,u
end


function main()
    a =0.0;
    b = 2.0;
    N::UInt16 = 10;
    y0 = 0.0;

    t1,u1 = euler(a,b,y0,N)
    t2,u2 = rungeKutta(a,b,y0,N)
    t3,u3 = adamsBashforth(a,b,y0,N)
    t4,u4 = adamsMoulton(a,b,y0,N)
    u = zeros(Float64, N+1)
    u[1] = y0[1]

    for i=1:N
        u[i+1] = 1-cos(t3[i+1])
    end
    

    print(u1)

    ylabel!("erro")
    xlabel!("t")
    

    # plot!(t3, u,label = "Analitica")
    # plot!(t1, u1, label = "Euler")
    # plot!(t2, u2, label = "Runge-Kutta")
    # plot!(t3, u3, label = "Adams-Bashforth")
    # plot!(t4, u4, label = "Adams-Moulton")

    # plot!(t1, u-u1,label = "erro Euler") 
    plot!(t2, u-u2,label = "erro Runge-Kutta") 
    # plot!(t3, u-u3,label = "erro Adams-Bashforth")
    # plot!(t4, u-u4,label = "erro Adams-Moulton")
    png("erro1000runge")

    
end

if length(ARGS)==0
    main()
end