// SPDX-License-Identifier: MIT

pragma solidity >=0.8.2 <0.9.0;

/**
 * @title Storage
 * @dev Store & retrieve value in a variable
 * @custom:dev-run-script ./scripts/deploy_with_ethers.ts
 */
contract Pret {

    uint quantity;

    /**
     * @dev Store value in variable
     * @param num value to store
     */
    function store(uint256 num) public {
        quantity = num;
    }

    /**
     * @dev Return value 
     * @return value of 'quantity'
     */
    function retrieve() public view returns (uint256){
        return quantity;
    }
}