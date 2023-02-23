select

xx.matricula,
xx.funcionario,
xx.cargo,
xx.setor,
xx.tipo,
xx.filial,

xx.peso_llg         as ll_peso,
xx.meta_llg         as ll_meta,
xx.atingido_llg     as ll_atingido,
xx.margem_llg       as ll_margem,
xx.peso_mkt         as ms_peso,
xx.meta_mkt         as ms_meta,
xx.atingido_mkt     as ms_atingido,	
xx.margem_mkt       as ms_margem,
xx.peso_exp         as ec_peso,
xx.meta_exp         as ec_meta,
xx.atingido_exp     as ec_atingido,
xx.margem_exp       as ec_margem,
xx.peso_dsp         as dv_peso,
xx.meta_dsp         as dv_meta,
xx.atingido_dsp     as dv_atingido,
xx.margem_dsp       as dv_margem,
xx.peso_orc         as oc_peso,
xx.meta_orc         as oc_meta,
xx.atingido_orc     as oc_atingido,
xx.margem_orc       as oc_margem,
xx.peso_ind         as ii_peso,
xx.meta_ind         as ii_meta,
xx.atingido_ind     as ii_atingido,
xx.margem_ind       as ii_margem,
xx.salario,
xx.total_margem     as margem_total,
xx.regua            as nome_regua,
(select csf.valor from main_classificacao csf where xx.total_margem between csf.minimo and csf.maximo and csf.regua_id = xx.regua_id) as valor_regua,
xx.salario * (select csf.valor from main_classificacao csf where xx.total_margem between csf.minimo and csf.maximo and csf.regua_id = xx.regua_id) as premio_total

from

(
    select x.*, 

    round((x.margem_llg + x.margem_exp + x.margem_orc + x.margem_dsp + x.margem_ind + x.margem_mkt), 2) as total_margem
    
    from 

    (
        select 

        a.codigo    as matricula,
        a.nome      as funcionario,
        b.cargo     as cargo,
        c.setor     as setor,
        c.tipo      as tipo,
        d.nome      as filial,
        e.regua     as regua,   
        e.id        as regua_id,
        a.salario   as salario,


        --LUCRO LIQUIDO GLOBAL
        f.peso      as peso_llg,
        f.meta      as meta_llg,
        l.margem    as atingido_llg,

        case 
            when l.margem <  f.meta                         then 0                  --Se o lucro liquido for menor que a meta eu perco tudo
            when l.margem >= 110                            then 27.5               --Se o lucro liquido passar 110% eu travo em 27,5
            when l.margem >= f.meta and l.margem < 110      then l.margem * 0.25    --Se o lucro liquido for entre minha meta e 110% eu aplico f(x) = 0,25x
        end         as margem_llg,
        --################################################################


        --MARKET SHARE (SE ATINGO MAIS OU IGUAL A META = PESO)
        g.peso      as peso_mkt,
        g.meta      as meta_mkt,
        m.margem    as atingido_mkt,

        case 
            when m.margem >= g.meta then g.peso
            else 0 
        end         as margem_mkt,
        --################################################################


        --EXPERIENCIA DO CLIENTE (SE ATINGO MAIS OU IGUAL A META = PESO)
        h.peso      as peso_exp,
        h.meta      as meta_exp,
        n.margem    as atingido_exp,

        case 
            when n.margem >= h.meta then h.peso
            else 0 
        end         as margem_exp,
        --################################################################


        --ORÇAMENTOS
        i.peso      as peso_orc,
        i.meta      as meta_orc,
        p.margem    as atingido_orc,

        case 
            when p.margem >= i.meta then 
                case 
                    when c.tipo = 'D' then 
                        case 
                            when p.margem <  i.meta                         then 22 --Se eu gastei menos do que minha meta eu ganho 22
                            when p.margem >= i.meta and p.margem <= 100     then 20 --Se eu gastei entre minha meta e o que foi orçado ganho 20
                            when p.margem >  100                            then 0  --Se eu gastei mais que o orçado eu perco tudo
                        end
                    when c.tipo = 'R' then 
                        case 
                            when p.margem <  i.meta                         then 0  --Se eu ganhei menos do que minha meta eu perco tudo
                            when p.margem >= i.meta and p.margem <= 100     then 20 --Se eu ganhei entre minha meta e o que foi orçado ganho 20
                            when p.margem >  100                            then 22 --Se eu ganhei mais que o orçado eu ganho 22
                        end
                end
            else 0 
        end         as margem_orc,
        --################################################################


        --DESPESA DE VENDA (SE ATINGO MENOS OU IGUAL A META = PESO)
        j.peso      as peso_dsp,
        j.meta      as meta_dsp,
        o.margem    as atingido_dsp,

        case 
            when o.margem <= j.meta then j.peso
            else 0 
        end         as margem_dsp,
        --################################################################


        --INDICADORES INDIVIDUAIS
        k.peso      as peso_ind,
        k.meta      as meta_ind,
        a.margem    as atingido_ind,

        case 
            when a.margem <  k.meta                         then 0                              --Se eu atingir menos que minha meta eu perco meu indicador
            when a.margem >= 100                            then 44                             --Se eu atingir mais que minha meta eu travo em 44
            when a.margem >= k.meta  and a.margem < 100     then (0.6684 * a.margem) - 22.831   --Se eu atingir entre minha meta e 100% eu aplico a f(x) = 0,6684x - 22,831
            
        end         as margem_ind
        --################################################################


        from        generator_funcionarios  a
        left join   main_cargos             b on b.id       = a.cargo_id 
        left join   main_setores            c on c.id       = b.setor_id 
        left join   main_filiais            d on d.id       = c.filial_id 
        left join   main_reguas             e on e.id       = b.regua_id 
        left join   main_regras             f on f.regra    = 'Lucro Líquido'
        left join   main_regras             g on g.regra    = 'MKT Share'
        left join   main_regras             h on h.regra    = 'EXP Cliente'
        left join   main_regras             i on i.regra    = 'Orçamento'
        left join   main_regras             j on j.regra    = 'Despesa/Venda'
        left join   main_regras             k on k.regra    = 'Individual'
        left join   generator_margens       l on l.regra_id = f.id
        left join   generator_margens       m on m.regra_id = g.id
        left join   generator_margens       n on n.regra_id = h.id
        left join   generator_margens       o on o.regra_id = j.id
        left join   generator_orcamentos    p on p.setor_id = c.id

    ) x

)

xx order by xx.funcionario