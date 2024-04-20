// SPDX-License-Identifier: MIT
pragma solidity >=0.8.2;

contract fructificateur {
    // Variables d'état
    uint256 public contractBalances = 0;

    struct ValeurClient {
        uint256 montant;
        uint256 duree; // en mois
        uint256 dureeRestante; // en mois
        uint256 tauxInteret; // taux d'intérêt en pourcentage
    }

    mapping(address => ValeurClient) public investisseur;
    mapping(address => ValeurClient) public emprunteur;
    
    address public owner;
    
    // Événement émis lorsqu'un pret est accorde
    event LoanGranted(address indexed borrower, uint256 amount, uint256 duration);

    // Constructeur
    constructor() {
        owner = msg.sender;
    }
    
    // Le taux d'interet en fonction de la duree en mois
    function findInterestRate(uint256 duration) public pure returns (uint256) { 
        require(duration > 0, "Duration must be greater than 0");

        uint256 interestRate;

        if (duration <= 6) {
            interestRate = 5; 
        } else if (duration <= 12) {
            interestRate = 8; 
        } else {
            interestRate = 10;
        }
        return interestRate;
    }

    // Prêter des fonds
    function investirFonds(uint256 duration) public payable {
        uint256 amount = msg.value;
        require(amount <= address(msg.sender).balance, "Insufficient funds to lend");
        require(amount > 0, "Amount must be greater than 0");
        require(duration > 0, "Duration must be greater than 0");

        uint256 tauxInteret = findInterestRate(duration);
        uint256 interest = (amount * duration * tauxInteret) / 100;
        require(interest > 0, "Interest must be greater than 0");

        contractBalances += amount;
        investisseur[msg.sender].montant += amount;
        investisseur[msg.sender].duree = duration; // en mois
        investisseur[msg.sender].dureeRestante = duration; // en mois
        investisseur[msg.sender].tauxInteret = tauxInteret;
        
        emit LoanGranted(msg.sender, amount, duration);
    }
    
    // Emprunter des fonds
    function emprunterFonds(uint256 amount, uint256 duration) public payable  {
        require(amount > 0, "Amount must be greater than 0");
        require(duration > 0, "Duration must be greater than 0");
        require(contractBalances >= amount, "Balance contrat insuffisante");
        require(address(this).balance >= amount, "Fond contrat insuffisant");
        
        uint256 tauxInteret = findInterestRate(duration);
        uint256 interest = (amount * duration * tauxInteret) / 100;
        require(address(msg.sender).balance >= interest, "Balance requise insuffisante pour recevoir le pret");
        

        payable(msg.sender).transfer(amount);
        contractBalances -= amount;
        
        emprunteur[msg.sender].montant += amount;
        emprunteur[msg.sender].duree = duration; // en mois
        emprunteur[msg.sender].dureeRestante = duration; // en mois
        emprunteur[msg.sender].tauxInteret = tauxInteret;

        emit LoanGranted(msg.sender, amount, duration);
    }

    // Remboursement mensuel
    function rembouserEmprunt() public payable {
        require(emprunteur[msg.sender].dureeRestante > 0, "Aucun pret actif trouve");
        uint256 amount = msg.value;

        // Calcul du montant à rembourser chaque mois (capital + intérêts)
        uint256 montantARembourser= (emprunteur[msg.sender].montant + (emprunteur[msg.sender].montant * emprunteur[msg.sender].tauxInteret / 100)) / emprunteur[msg.sender].duree;
        require(montantARembourser <= address(msg.sender).balance, "Balance insuffisante");
        require(montantARembourser <= amount, "Valeur envoyee avec la transaction est insuffisante");

        // rembourse au cas ca depasse montantARembourser
        payable(address(msg.sender)).transfer(amount-montantARembourser);
        
        contractBalances += montantARembourser;
        emprunteur[msg.sender].dureeRestante--;
        
        if (emprunteur[msg.sender].dureeRestante == 0) {
            delete emprunteur[msg.sender];
        }
    }

    // recuperation de l'investissement mensuel
    function retourInvestissement() public payable {
        require(investisseur[msg.sender].dureeRestante > 0, "Aucun pret actif trouve");
        
        // Calcul du montant à rembourser chaque mois (capital + intérêts)
        uint256 montantARecevoir = (investisseur[msg.sender].montant + (investisseur[msg.sender].montant * investisseur[msg.sender].tauxInteret / 100)) / investisseur[msg.sender].duree;
        
        // Transfert du montant remboursé à l'investisseur
        require(contractBalances >= montantARecevoir, "Balance contrat insuffisante");
        require(address(this).balance >= montantARecevoir, "Fond du contract insuffisant");
        
        payable(msg.sender).transfer(montantARecevoir);
        investisseur[msg.sender].dureeRestante--;
        contractBalances -= montantARecevoir;
        
        if (investisseur[msg.sender].dureeRestante == 0) {
            delete investisseur[msg.sender];
        }
    }
        
    function getContractBalance() public view returns (uint256) {
        return contractBalances;
    }

    function getContractBalanceReelle() public view returns (uint256) {
        return address(this).balance;
    }

    //setContractBalances
    function addFondContractBalances(uint256 _contractBalances) public onlyOwner payable{
        contractBalances += _contractBalances;
    }

    // Modificateur pour verifier si le message sender est le proprietaire du contrat
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
}