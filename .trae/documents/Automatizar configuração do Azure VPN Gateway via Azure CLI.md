## Objetivo
Configurar um Azure VPN Gateway (Site‑to‑Site e opcional VNet‑to‑VNet) usando Azure CLI com segurança, validando conectividade e BGP quando necessário. Entregar comandos prontos, verificações e boas práticas.

## Pré‑requisitos
1. Assinatura do Azure ativa e permissão para criar recursos.
2. Azure CLI instalado e autenticado: `az login` e `az account set --subscription <SUB_ID_OR_NAME>`.
3. Planejamento de endereços IP sem sobreposição:
   - VNet: `10.1.0.0/16`
   - Subrede de app: `FrontEnd` `10.1.0.0/24`
   - `GatewaySubnet` com /27 ou maior: `10.1.255.0/27`
4. IP público externo do dispositivo VPN on‑prem e prefixos locais (ex.: `192.168.0.0/16,10.0.0.0/16`).

## Passos (Portal ou CLI)
### 1) Grupo de recursos
- `az group create -n TestRG1 -l eastus`

### 2) Rede virtual e subredes
- `az network vnet create -g TestRG1 -n VNet1 --address-prefix 10.1.0.0/16 --subnet-name FrontEnd --subnet-prefix 10.1.0.0/24`
- `az network vnet subnet create -g TestRG1 --vnet-name VNet1 -n GatewaySubnet --address-prefix 10.1.255.0/27`
  - Não associar NSG à `GatewaySubnet`.

### 3) IP público para o gateway
- `az network public-ip create -g TestRG1 -n VpnGwPip1 --sku Standard --allocation-method Static`
  - Para ativo‑ativo, criar dois IPs e usar `--public-ip-addresses` no passo seguinte.

### 4) VPN Gateway
- `az network vnet-gateway create -g TestRG1 -n VNet1-Gateway --public-ip-address VpnGwPip1 --vnet VNet1 --gateway-type Vpn --vpn-type RouteBased --sku VpnGw2AZ --vpn-gateway-generation Generation2`
  - Criação leva ~45 min.
  - Ativo‑ativo: `--enable-active-active true` e dois IPs.
  - BGP opcional: adicionar `--asn 65010` (ajuste conforme sua política).

### 5) Local Network Gateway (on‑prem)
- `az network local-gateway create -g TestRG1 -n OnPrem --gateway-ip-address <IP_PUBLICO_ONPREM> --local-address-prefixes <PREFIXOS_LOCAL>`
  - Com BGP: `--asn 65020 --bgp-peering-address <IP_BGP_ONPREM>`.

### 6) Conexão Site‑to‑Site
- `az network vpn-connection create -g TestRG1 -n VNet1-To-OnPrem --vnet-gateway1 VNet1-Gateway --local-gateway2 OnPrem --shared-key <PSK>`
  - Com BGP: adicionar `--enable-bgp true`.

### 7) VNet‑to‑VNet (opcional)
- Criar `VNet2`, `GatewaySubnet`, IP público e `VNet2-Gateway`.
- Conexão:
  - `az network vpn-connection create -g TestRG1 -n VNet1-To-VNet2 --vnet-gateway1 VNet1-Gateway --vnet-gateway2 VNet2-Gateway --shared-key <PSK>`

## Verificação
- Status da conexão: `az network vpn-connection show -g TestRG1 -n VNet1-To-OnPrem --query connectionStatus -o tsv`
- Métricas/logs: Azure Monitor e diagnóstico do gateway.

## Boas práticas
- Sem NSG na `GatewaySubnet`.
- Se usar DNS personalizado na VNet, garantir encaminhamento ao DNS do Azure `168.63.129.16` para o plano de controle do gateway.
- Planejar custos: IP público, SKU do gateway (ex.: `VpnGw2AZ`).
- Documentar PSK e rotas; evitar sobreposições de prefixos.

## Como o agente pode automatizar
- Executar os comandos acima no seu terminal após `az login` (o agente pode usar o navegador embutido para completar o device‑code).
- Pausar em pontos críticos (criação de gateway) e retomar quando a implantação concluir.
- Validar `connectionStatus` e capturar evidências.

## Entregáveis
1) Scripts CLI parametrizados (S2S e VNet‑to‑VNet).
2) Checklist de verificação e evidências.
3) Guia de rollback (exclusão dos recursos se necessário).

Confirme para que eu execute com os valores do seu ambiente (assinatura, região, IP on‑prem, prefixos, PSK e se deseja BGP/ativo‑ativo).