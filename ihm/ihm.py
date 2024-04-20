import base64
import web3
from eth_utils import to_checksum_address
import json


class WalletManager:
    def __init__(self):
        self.w3 = self.__create_web3_instance()
        self.account = '0xe23B903Cd74F630fD87d504119682E3442f3D511'
        self.account_private_key = 'ma clé privée que je ne vais pas vous donner'
        self.max_fee_per_gas = self.w3.to_wei('250000000000000', 'wei')
        self.gas_limit = 3000000
        self.max_priority_fee_per_gas = self.w3.eth.max_priority_fee
        self.chain_id = 11155111
        self.contract_address = '0xe4fBeC2953aA37e70451e70FCbad56E2ff9b8196'

        with open('../ABI/ABI.json', 'r') as abi_file:
            self.contract_abi = json.load(abi_file)
        self.contract = self.w3.eth.contract(address=to_checksum_address(self.contract_address), abi=self.contract_abi)

    @staticmethod
    def __create_web3_instance():
        infura_api_key = 'd7673ea500d44f6db368563a06856b57'
        infura_api_key_secret = 'ma clé privée que je ne vais pas vous donner'
        data = f'{infura_api_key}:{infura_api_key_secret}'.encode('ascii')
        basic_auth_token = base64.b64encode(data).strip().decode('utf-8')

        infura_sepolia_endpoint = f'https://sepolia.infura.io/v3/ma clée api infura que je ne vais pas vous donner'

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

        tx = self.contract.functions.investirFonds(duration).build_transaction(
            self.get_tansaction_dict(self.gas_limit, amount))
        tx_hash = self.send_and_sign_tx(tx)

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction réussie. Montant investi:", amount, "TX Hash:", tx_hash.hex())

    def emprunter_fonds(self):
        duration = int(input("Entrez la durée en mois: "))
        amount = int(input("Entrez le montant à emprunter: "))

        tx = self.contract.functions.emprunterFonds(amount, duration).build_transaction(
            self.get_tansaction_dict(self.gas_limit, 0))
        # nonce = self.w3.eth.get_transaction_count(to_checksum_address(self.account))
        # tx['nonce'] = nonce
        tx_hash = self.send_and_sign_tx(tx)

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction réussie. Montant emprunté:", amount, "TX Hash:", tx_hash.hex())

    def retour_investissement(self):
        tx = self.contract.functions.retourInvestissement().build_transaction(
            self.get_tansaction_dict(self.gas_limit, 0))
        tx_hash = self.send_and_sign_tx(tx)

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction envoyé.", "TX Hash:", tx_hash.hex())

    def rembourser_emprunt(self):
        amount = self.contract.functions.recupererMontantARembourser().call({'from': self.account})
        tx = self.contract.functions.rembouserEmprunt().build_transaction(
            self.get_tansaction_dict(self.gas_limit, amount))
        tx_hash = self.send_and_sign_tx(tx)

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction envoyé.\nGas utilisé", receipt['gasUsed'], " Tx Hash:", tx_hash.hex())

    def add_fond_contract_balance(self):
        new_balance = int(input("Entrez le solde a ajouter contrat en wei: "))

        old_balance = self.contract.functions.getContractBalance().call()
        # Détermine le prix du gaz
        tx = self.contract.functions.addFondContractBalances(new_balance).build_transaction(
            self.get_tansaction_dict(self.gas_limit, new_balance))

        tx_hash = self.send_and_sign_tx(tx)
        print("Transaction réussie. Nouveau solde du contrat:", old_balance + new_balance, "\nTX Hash:", tx_hash.hex())

    def send_and_sign_tx(self, tx):
        # Signe la transaction avec la clé privée du propriétaire
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account_private_key)

        # Envoie la transaction signée
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash

    def get_tansaction_dict(self, gas_limit, amount):
        return {
            'chainId': self.chain_id,  # Mettez l'ID de la chaîne Ethereum correspondant ici
            'gas': gas_limit,
            'value': self.w3.to_wei(amount, 'wei'),  # Montant d'Ether à envoyer vers le contrat
            'nonce': self.w3.eth.get_transaction_count(to_checksum_address(self.account)),
        }


# Main function
def main():
    print("\nBienvenue dans l'interface console pour le contrat Ethereum Fructificateur.")
    wm = WalletManager()
    while True:
        print("\n\n================================")
        print("0. Ontenir ma balance")
        print("1. Obtenir la balance du contrat")
        print("2. Investir des fonds")
        print("3. Emprunter des fonds")
        print("4. Retourner l'investissement")
        print("5. Rembourser un emprunt")
        print("6. Ajouter du solde au contrat")
        print("7. Quitter")
        choice = input("Entrez votre choix: ")
        if choice == '0':
            print("Votre balance est de", wm.w3.eth.get_balance(to_checksum_address(wm.account)), "wei")
        elif choice == '1':
            wm.show_contract_balance()
        elif choice == '2':
            wm.investir_fonds()
        elif choice == '3':
            wm.emprunter_fonds()
        elif choice == '4':
            wm.retour_investissement()
        elif choice == '5':
            wm.rembourser_emprunt()
        elif choice == '6':
            wm.add_fond_contract_balance()
        elif choice == '7':
            print("Merci d'avoir utilisé l'interface.")
            break
        else:
            print("Choix invalide. Veuillez entrer un numéro valide.")


if __name__ == "__main__":
    main()
