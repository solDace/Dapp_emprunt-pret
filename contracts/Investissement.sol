// SPDX-License-Identifier: MIT

pragma solidity >=0.8.2 <0.9.0;

/**
 * @title Storage
 * @dev Store & retrieve value in a variable
 * @custom:dev-run-script ./scripts/deploy_with_ethers.ts
 */
contract ContratInvestissement {
    struct Investissement {
        address investisseur;
        uint256 montant;
        uint256 duree; // en mois
        uint256 dureeRestante; // en mois
        uint256 tauxInteret; // taux d'intérêt en pourcentage
        uint256 tempsDebut;
        bool actif;
    }


    mapping(address => Investissement) public investissements;

       function demanderIvestissement(uint256 _montant, uint256 _duree) external payable {
        require(_montant > address(this).balance, "Fonds insuffisants dans le contrat");
        require(_duree > 0, "La duree doit etre superieure a zero");
        require(!investissements[msg.sender].actif, "Vous avez deja un investissement actif");

        // Calcul du taux d'intérêt en fonction de la durée demandée
        uint256 tauxInteret = calculerTauxInteret(_duree);
        
        investissements[msg.sender] = Investissement({
            investisseur: msg.sender,
            montant: _montant,
            duree: _duree,
            dureeRestante: _duree,
            tauxInteret: tauxInteret,
            tempsDebut: block.timestamp,
            actif: true
        });
    }

    function recevoirRemboursement() external {
        Investissement storage investissement = investissements[msg.sender];
        require(investissement.actif, "Aucun pret actif trouve");
        
        // Calcul du montant à rembourser chaque mois (capital + intérêts)
        uint256 montantARecevoir = investissement.montant + (investissement.montant * investissement.tauxInteret / 100) / investissement.duree;
        
        // Transfert du montant remboursé à l'investisseur
        payable(msg.sender).transfer(montantARecevoir);

        // Vérification si le prêt est remboursé
        if (investissement.dureeRestante == 1) {
            investissement.actif = false;
        } else {
            investissement.dureeRestante--;
        }
    }

    function calculerTauxInteret(uint256 _duree) internal pure returns (uint256) {
        // Plus la durée est longue, plus le taux d'intérêt est élevé
        if (_duree <= 6) {
            return 5; // 5% d'intérêt pour les prêts de 6 mois ou moins
        } else if (_duree <= 12) {
            return 7; // 7% d'intérêt pour les prêts de plus de 6 mois à 12 mois
        } else {
            return 10; // 10% d'intérêt pour les prêts de plus de 12 mois
        }
    }

}