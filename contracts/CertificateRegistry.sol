// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title CertificateRegistry
/// @notice Minimal demo registry for certificate fingerprints.
/// Store hashes and minimal references only; never store personal data or files.
contract CertificateRegistry {
    address public owner;
    uint256 public nextRecordId = 1;

    struct Record {
        bytes32 documentHash;
        address issuer;
        uint256 timestamp;
        bool revoked;
    }

    mapping(uint256 => Record) private records;
    mapping(address => bool) public authorizedIssuers;

    event IssuerAuthorizationChanged(address indexed issuer, bool authorized);
    event CertificateRegistered(
        uint256 indexed recordId,
        bytes32 indexed documentHash,
        address indexed issuer,
        uint256 timestamp
    );
    event CertificateRevoked(uint256 indexed recordId, address indexed issuer);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    modifier onlyIssuer() {
        require(authorizedIssuers[msg.sender], "Not an authorized issuer");
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedIssuers[msg.sender] = true;
        emit IssuerAuthorizationChanged(msg.sender, true);
    }

    function setIssuer(address issuer, bool authorized) external onlyOwner {
        require(issuer != address(0), "Invalid address");
        authorizedIssuers[issuer] = authorized;
        emit IssuerAuthorizationChanged(issuer, authorized);
    }

    function registerCertificate(bytes32 documentHash) external onlyIssuer returns (uint256) {
        require(documentHash != bytes32(0), "Empty document hash");
        uint256 recordId = nextRecordId++;
        records[recordId] = Record(documentHash, msg.sender, block.timestamp, false);
        emit CertificateRegistered(recordId, documentHash, msg.sender, block.timestamp);
        return recordId;
    }

    function verifyCertificate(uint256 recordId, bytes32 submittedHash)
        external view returns (bool matchFound, bool revoked, address issuer, uint256 timestamp)
    {
        Record memory record = records[recordId];
        require(record.timestamp != 0, "Record not found");
        return (
            record.documentHash == submittedHash,
            record.revoked,
            record.issuer,
            record.timestamp
        );
    }

    function revokeCertificate(uint256 recordId) external {
        Record storage record = records[recordId];
        require(record.timestamp != 0, "Record not found");
        require(msg.sender == owner || msg.sender == record.issuer, "Not permitted");
        require(!record.revoked, "Already revoked");
        record.revoked = true;
        emit CertificateRevoked(recordId, msg.sender);
    }

    function getRecord(uint256 recordId)
        external view returns (bytes32 documentHash, address issuer, uint256 timestamp, bool revoked)
    {
        Record memory record = records[recordId];
        require(record.timestamp != 0, "Record not found");
        return (record.documentHash, record.issuer, record.timestamp, record.revoked);
    }
}
