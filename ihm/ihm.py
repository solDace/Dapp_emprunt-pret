import base64
import web3
from eth_utils import to_checksum_address
import json


class WalletManager:
    def __init__(self):
        self.w3 = self.__create_web3_instance()
        self.account = '0xe23B903Cd74F630fD87d504119682E3442f3D511'
        self.account_private_key = 'b1d09f45f78e87a0227120b3e0ab2da7519b1cb258047965a54a8228e01620c0'
        self.max_fee_per_gas = self.w3.to_wei('250', 'gwei')
        self.max_priority_fee_per_gas = self.w3.eth.max_priority_fee
        self.chain_id = 11155111
        self.contract_address = '0x3F2c73a8be1385867d22e80668A125Cbd738f9Ab'

        with open('../ABI/ABI.json', 'r') as abi_file:
            self.contract_abi = json.load(abi_file)
        self.contract = self.w3.eth.contract(address=to_checksum_address(self.contract_address), abi=self.contract_abi)

    @staticmethod
    def __create_web3_instance():
        infura_api_key = 'd7673ea500d44f6db368563a06856b57'
        infura_api_key_secret = 'LWCY9XwWRyaZSLWtkncXYz6SQNqtoAXwhWDkthkDQ2amRYktyDAlyg'
        data = f'{infura_api_key}:{infura_api_key_secret}'.encode('ascii')
        basic_auth_token = base64.b64encode(data).strip().decode('utf-8')

        infura_sepolia_endpoint = f'https://sepolia.infura.io/v3/d7673ea500d44f6db368563a06856b57'

        headers = dict(Authorization=f'Basic {basic_auth_token}')
        return web3.Web3(web3.HTTPProvider(infura_sepolia_endpoint, request_kwargs=dict(headers=headers)))

    def send_eth(self, target_account, amount, unit='wei'):
        if unit != 'wei':
            amount = self.w3.to_wei(amount, unit)

        nonce = self.w3.eth.get_transaction_count(to_checksum_address(self.account))
        tx = {'nonce': nonce,
              'maxFeePerGas': self.max_fee_per_gas,
              'maxPriorityFeePerGas': self.max_priority_fee_per_gas,
              'from': self.account,
              'to': target_account,
              'value': amount,
              'data': b'',
              'type': 2,
              'chainId': self.chain_id}
        tx['gas'] = self.w3.eth.estimate_gas(tx)

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account_private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        result = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if result['status'] != 1:
            raise RuntimeError('transaction failed: {tx_hash}')

    def show_contract_balance(self):
        balance = self.contract.functions.getContractBalance().call()
        balance_reelle = self.contract.functions.getContractBalanceReelle().call()
        print("Balance du contrat:", balance)
        print("Balance reelle du contrat:", balance_reelle)

    def investir_fonds(self):
        duration = int(input("Entrez la durée en mois: "))
        amount = int(input("Entrez le montant à investir: "))
        tx_hash = self.contract.functions.investirFonds(duration).transact({'from': self.account, 'value': amount})
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction réussie. Montant investi:", amount, "TX Hash:", tx_hash.hex())

    def emprunter_fonds(self):
        duration = int(input("Entrez la durée en mois: "))
        amount = int(input("Entrez le montant à emprunter: "))
        tx_hash = self.contract.functions.emprunterFonds(amount, duration).transact(
            {'from': self.account, 'value': amount})
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction réussie. Montant emprunté:", amount, "TX Hash:", tx_hash.hex())

    def rembourser_emprunt(self):
        tx_hash = self.contract.functions.rembouserEmprunt().transact({'from': self.account, 'value': 0})
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction réussie. Montant remboursé:", receipt['gasUsed'], "TX Hash:", tx_hash.hex())

    def retour_investissement(self):
        tx_hash = self.contract.functions.retourInvestissement().transact({'from': self.account, 'value': 0})
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction réussie. Montant retourné:", receipt['gasUsed'], "TX Hash:", tx_hash.hex())

    def add_fond_contract_balance(self):
        new_balance = int(input("Entrez le solde a ajouter contrat en wei: "))
        gas_limit = 100000

        old_balance = self.contract.functions.getContractBalance().call()
        # Détermine le prix du gaz
        tx = self.contract.functions.addFondContractBalances(new_balance).build_transaction(
            self.get_tansaction_dict(gas_limit, new_balance))

        tx_hash = self.send_and_sign_tx(tx)
        print("Transaction réussie. Nouveau solde du contrat:", old_balance + new_balance, "\nTX Hash:", tx_hash.hex())

    def send_and_sign_tx(self, tx):
        # Signe la transaction avec la clé privée du propriétaire
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account_private_key)
        # Envoie la transaction signée
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash

    def get_tansaction_dict(self, gas_limit, new_balance):
        return {
            'chainId': self.chain_id,  # Mettez l'ID de la chaîne Ethereum correspondant ici
            'gas': gas_limit,
            'value': self.w3.to_wei(new_balance, 'wei'),  # Montant d'Ether à envoyer vers le contrat
            'nonce': self.w3.eth.get_transaction_count(to_checksum_address(self.account)),
        }


# Main function
def main():
    print("\nBienvenue dans l'interface console pour le contrat Ethereum Fructificateur.")
    wm = WalletManager()
    while True:
        print("\n\n================================")
        print("1. Obtenir la balance du contrat")
        print("2. Investir des fonds")
        print("3. Emprunter des fonds")
        print("4. Rembourser un emprunt")
        print("5. Retourner l'investissement")
        print("6. Ajouter du solde au contrat")
        print("7. Quitter")
        choice = input("Entrez votre choix: ")
        if choice == '1':
            wm.show_contract_balance()
        elif choice == '2':
            wm.investir_fonds()
        elif choice == '3':
            wm.emprunter_fonds()
        elif choice == '4':
            wm.rembourser_emprunt()
        elif choice == '5':
            wm.retour_investissement()
        elif choice == '6':
            wm.add_fond_contract_balance()
        elif choice == '7':
            print("Merci d'avoir utilisé l'interface.")
            break
        else:
            print("Choix invalide. Veuillez entrer un numéro valide.")


if __name__ == "__main__":
    main()
