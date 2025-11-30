# main.py
import asyncio
import csv
from faker import Faker
from config.settings import DATAIMPULSE_PROXY, MAX_CONCURRENCY
from core.browser_manager import search_loop_task_single_proxy
from search.address_searcher import generate_addresses

fake = Faker('en_US')

async def main():
    addresses = generate_addresses(100)
    results_queue = asyncio.Queue()
    
    print(f"🎯 Criando {MAX_CONCURRENCY} instâncias isoladas com proxy rotativo...")
     
    address_chunks = [[] for _ in range(MAX_CONCURRENCY)]
    for i, addr in enumerate(addresses):
        address_chunks[i % MAX_CONCURRENCY].append(addr)
    
    tasks = []
    for i in range(MAX_CONCURRENCY):
        if address_chunks[i]:
            task = asyncio.create_task(
                search_loop_task_single_proxy(DATAIMPULSE_PROXY, address_chunks[i], results_queue)
            )
            tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)
    
    final_results = []
    while not results_queue.empty():
        final_results.append(await results_queue.get())
    
    output_file = 'resultados_proxies_rotativos.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Endereço', 'Nome', 'Telefone'])
        success_count = 0
        for item in final_results:
            address, name, phone = item
            writer.writerow([address, name or 'N/A', phone or 'N/A'])
            if name and name != 'N/A':
                success_count += 1

    print(f"\n✅ CONCLUÍDO!")
    print(f"📊 Sucessos: {success_count}/{len(final_results)}")
    print(f"🎯 Instâncias isoladas: {MAX_CONCURRENCY}")
    print(f"💾 Arquivo: {output_file}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Parado")
    except Exception as e:
        print(f"\n💥 Erro: {e}")