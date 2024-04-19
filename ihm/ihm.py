from web3 import Web3
import json

# Connexion à un fournisseur Ethereum
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))  # Mettez votre fournisseur Ethereum ici

# Adresse de votre contrat
contract_address = '0x123456789ABCDEF...'

# Adresse du compte qui interagit avec le contrat
account_address = '0xABCDEF123456789...'

# Chargement du contrat ABI
with open('contracts/artifacts/fructificateur.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

# Instanciation du contrat
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Exemple d'appel de fonction sur le contrat
def get_contract_balance():
    balance = contract.functions.getContractBalance().call()
    print("Balance du contrat:", balance)

def investir_fonds():
    duration = int(input("Entrez la durée en mois: "))
    amount = int(input("Entrez le montant à investir: "))
    tx_hash = contract.functions.investirFonds(duration).transact({'from': account_address, 'value': amount})
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    print("Transaction réussie. Montant investi:", amount, "TX Hash:", tx_hash.hex())

def emprunter_fonds():
    duration = int(input("Entrez la durée en mois: "))
    amount = int(input("Entrez le montant à emprunter: "))
    tx_hash = contract.functions.emprunterFonds(amount, duration).transact({'from': account_address, 'value': amount})
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    print("Transaction réussie. Montant emprunté:", amount, "TX Hash:", tx_hash.hex())

def rembourser_emprunt():
    tx_hash = contract.functions.rembouserEmprunt().transact({'from': account_address, 'value': 0})
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    print("Transaction réussie. Montant remboursé:", receipt['gasUsed'], "TX Hash:", tx_hash.hex())

def retour_investissement():
    tx_hash = contract.functions.retourInvestissement().transact({'from': account_address, 'value': 0})
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    print("Transaction réussie. Montant retourné:", receipt['gasUsed'], "TX Hash:", tx_hash.hex())

def set_contract_balance():
    new_balance = int(input("Entrez le nouveau solde du contrat: "))
    tx_hash = contract.functions.setContractBalances(new_balance).transact({'from': account_address})
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    print("Transaction réussie. Nouveau solde du contrat:", new_balance, "TX Hash:", tx_hash.hex())

# Main function
def main():
    print("Bienvenue dans l'interface console pour le contrat Ethereum.")
    while True:
        print("1. Obtenir la balance du contrat")
        print("2. Investir des fonds")
        print("3. Emprunter des fonds")
        print("4. Rembourser un emprunt")
        print("5. Retourner l'investissement")
        print("6. Modifier le solde du contrat")
        print("7. Quitter")
        choice = input("Entrez votre choix: ")
        if choice == '1':
            get_contract_balance()
        elif choice == '2':
            investir_fonds()
        elif choice == '3':
            emprunter_fonds()
        elif choice == '4':
            rembourser_emprunt()
        elif choice == '5':
            retour_investissement()
        elif choice == '6':
            set_contract_balance()
        elif choice == '7':
            print("Merci d'avoir utilisé l'interface.")
            break
        else:
            print("Choix invalide. Veuillez entrer un numéro valide.")

if __name__ == "__main__":
    main()